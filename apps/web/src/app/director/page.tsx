import { DirectorPanel } from "@/components/director-panel";
import { fetchDirectorPanel } from "@/lib/api";

export default async function DirectorPage() {
  const panel = await fetchDirectorPanel();

  return (
    <main className="space-y-8">
      <DirectorPanel initialPanel={panel} />
    </main>
  );
}
