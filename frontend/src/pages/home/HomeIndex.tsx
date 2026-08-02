// features
import { ProfileCard } from "@/features/profile/ui/ProfileCard";

/** Home landing content showing the current user's profile. */
export default function HomeIndex() {
  return (
    <div className="flex flex-1 items-center justify-center px-6 py-10">
      <ProfileCard />
    </div>
  );
}
