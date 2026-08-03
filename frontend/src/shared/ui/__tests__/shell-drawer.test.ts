import { useShellDrawer } from "../shell-drawer";

describe("useShellDrawer", () => {
  beforeEach(() => {
    useShellDrawer.setState({ isServersOpen: false, isFriendsOpen: false });
  });

  it("opens a drawer", () => {
    useShellDrawer.getState().openServers();
    expect(useShellDrawer.getState().isServersOpen).toBe(true);
  });

  it("keeps only one drawer open at a time", () => {
    useShellDrawer.getState().openServers();
    useShellDrawer.getState().openFriends();
    expect(useShellDrawer.getState().isServersOpen).toBe(false);
    expect(useShellDrawer.getState().isFriendsOpen).toBe(true);
  });

  it("toggles a drawer", () => {
    useShellDrawer.getState().toggleFriends();
    expect(useShellDrawer.getState().isFriendsOpen).toBe(true);
    useShellDrawer.getState().toggleFriends();
    expect(useShellDrawer.getState().isFriendsOpen).toBe(false);
  });

  it("closes all drawers", () => {
    useShellDrawer.getState().openFriends();
    useShellDrawer.getState().closeAll();
    expect(useShellDrawer.getState().isFriendsOpen).toBe(false);
    expect(useShellDrawer.getState().isServersOpen).toBe(false);
  });
});
