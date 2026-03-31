import { CharacterManagementPanel } from "@/components/character-management-panel";
import { fetchCharacters } from "@/lib/api";

export default async function CharactersPage() {
  const characters = await fetchCharacters();

  return (
    <main className="space-y-8">
      <CharacterManagementPanel initialCharacters={characters} />
    </main>
  );
}
