export type NoteData = {
  id: string;
  content: string;
  date: number;
};

const loadLocalNotes = (sortByDate: boolean): NoteData[] => {
  const localNotes: NoteData[] = Object.keys(localStorage)
    .filter((key) => key.startsWith("note-"))
    .map((key) => JSON.parse(localStorage.getItem(key) as string));
  if (sortByDate) {
    localNotes.sort((a, b) => b.date - a.date);
  }
  return localNotes;
};

/**
 * Clean the out of date notes if there are more than 10 notes
 */
const cleanOutdatedNotes = () => {
  const localNotes: NoteData[] = loadLocalNotes(true);
  if (localNotes.length > 10) {
    localNotes.slice(10).forEach((note) => {
      console.log("Note Deleted with Id: ", note.id);
      localStorage.removeItem("note-" + note.id);
    });
  }
};

const loadMostRecentNote = (): NoteData => {
  const localNotes: NoteData[] = loadLocalNotes(false);
  const mostRecentNote: NoteData = localNotes.reduce((prev, curr) => {
    return prev.date >= curr.date ? prev : curr;
  });
  return mostRecentNote;
};

export { loadLocalNotes, cleanOutdatedNotes, loadMostRecentNote };
