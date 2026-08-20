"""job_indexes + job_details -> job_postings/skills/job_posting_skills 데이터 이관.

멱등(idempotent)하게 작성됨: 이미 이관된 source_id는 건너뜀 -> 여러 번 실행해도 안전.
"""
import logging

from app.database import SessionLocal
from app.models import (
    JobCategory,
    JobDetail,
    JobIndex,
    JobPosting,
    JobPostingCategory,
    JobPostingSkill,
    PostingStatus,
    Skill,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

SOURCE = "saramin"


def get_or_create(db, cache: dict[str, object], model, name: str):
    name = name.strip()
    if name in cache:
        return cache[name]

    obj = db.query(model).filter(model.name == name).first()
    if not obj:
        obj = model(name=name)
        db.add(obj)
        db.flush()  # id 확보 (커밋 전에도 FK로 참조 가능하게)

    cache[name] = obj
    return obj


def resolve_status(job_detail: JobDetail | None) -> PostingStatus:
    if job_detail is None:
        return PostingStatus.PENDING
    if job_detail.is_failed:
        return PostingStatus.FAILED
    return PostingStatus.CRAWLED


def group_by_rec_idx(indexes: list[JobIndex]) -> dict[str, list[JobIndex]]:
    """같은 rec_idx가 여러 job_name(카테고리)에 걸쳐 중복 저장돼 있어 rec_idx 기준으로 묶음."""
    groups: dict[str, list[JobIndex]] = {}
    for idx in indexes:
        groups.setdefault(idx.rec_idx, []).append(idx)
    return groups


def main():
    db = SessionLocal()
    skill_cache: dict[str, Skill] = {}
    category_cache: dict[str, JobCategory] = {}

    already_migrated = set(
        r[0] for r in db.query(JobPosting.source_id).filter(JobPosting.source == SOURCE).all()
    )
    logger.info("이미 이관된 posting %d건, 스킵 예정", len(already_migrated))

    details_by_href = {d.href: d for d in db.query(JobDetail).all()}
    logger.info("job_details %d건 로드", len(details_by_href))

    groups = group_by_rec_idx(db.query(JobIndex).all())
    logger.info("job_indexes %d건 -> rec_idx 기준 %d개 posting으로 이관 시작", sum(len(v) for v in groups.values()), len(groups))

    migrated, skipped, skill_links, category_links = 0, 0, 0, 0

    for i, (rec_idx, rows) in enumerate(groups.items()):
        if rec_idx in already_migrated:
            skipped += 1
            continue

        primary = rows[0]
        detail = details_by_href.get(primary.href)

        posting = JobPosting(
            source=SOURCE,
            source_id=rec_idx,
            company=primary.company,
            title=primary.title,
            url=primary.href,
            status=resolve_status(detail),
            content=detail.content if detail else None,
            indexed_at=min(r.crawled_at for r in rows if r.crawled_at is not None) if any(r.crawled_at for r in rows) else None,
            crawled_at=detail.created_at if detail else None,
        )
        db.add(posting)
        db.flush()  # posting.id 확보

        for row in rows:
            if not row.job_name:
                continue
            category = get_or_create(db, category_cache, JobCategory, row.job_name)
            exists = db.query(JobPostingCategory).filter_by(
                job_posting_id=posting.id, category_id=category.id
            ).first()
            if not exists:
                db.add(JobPostingCategory(job_posting_id=posting.id, category_id=category.id))
                category_links += 1

        if detail and detail.tech_stack:
            for tech in detail.tech_stack.split(","):
                tech = tech.strip()
                if not tech:
                    continue
                skill = get_or_create(db, skill_cache, Skill, tech)
                exists = db.query(JobPostingSkill).filter_by(
                    job_posting_id=posting.id, skill_id=skill.id
                ).first()
                if not exists:
                    db.add(JobPostingSkill(job_posting_id=posting.id, skill_id=skill.id))
                    skill_links += 1

        migrated += 1
        already_migrated.add(rec_idx)

        if (i + 1) % 500 == 0:
            db.commit()
            logger.info("%d/%d posting 처리 (이관 %d, 스킵 %d)", i + 1, len(groups), migrated, skipped)

    db.commit()
    logger.info(
        "완료: job_postings %d건 신규 이관, %d건 스킵(이미 존재), "
        "category 연결 %d건(종류 %d개), skill 연결 %d건(종류 %d개)",
        migrated, skipped, category_links, len(category_cache), skill_links, len(skill_cache),
    )
    db.close()


if __name__ == "__main__":
    main()
