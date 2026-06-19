import { create } from "zustand";
import { combine } from "zustand/middleware";

type State = {
  selectedRole: string;
};

const initialState: State = {
  selectedRole: "all",
};

const useSelectedRoleStore = create(
  combine(initialState, (set) => ({
    actions: {
      setSelectedRole: (role) => set({ selectedRole: role }),
    },
  })),
);

export const useSelectedRole = () => {
  const seletedRole = useSelectedRoleStore((store) => store.selectedRole);
  return seletedRole;
};
export const useSetSelectedRole = () => {
  const setSelectedRole = useSelectedRoleStore(
    (store) => store.actions.setSelectedRole,
  );
  return setSelectedRole;
};
