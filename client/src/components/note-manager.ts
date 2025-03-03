export type NoteData = {
  id: string;
  content: string;
  date: string;
};

const loadLocalNotes = (): NoteData[] => {
  const localNotes: NoteData[] = Object.keys(localStorage)
    .filter((key) => key.startsWith("note-"))
    .map((key) => JSON.parse(localStorage.getItem(key) as string));
  return localNotes;
};

/**
 * Clean the out of date notes if there are more than 10 notes
 */
const cleanOutdatedNotes = () => {
  const localNotes: NoteData[] = loadLocalNotes();
  if (localNotes.length > 10) {
    const sortedNotes: NoteData[] = localNotes.sort(
      (a, b) => parseInt(b.date) - parseInt(a.date),
    );
    sortedNotes.slice(10).forEach((note) => {
      localStorage.removeItem("note-" + note.id);
    });
  }
};

const loadMostRecentNote = (): NoteData => {
  const localNotes: NoteData[] = loadLocalNotes();
  const mostRecentNote: NoteData = localNotes.reduce((prev, curr) => {
    return prev.date >= curr.date ? prev : curr;
  });
  return mostRecentNote;
};

export { loadLocalNotes, cleanOutdatedNotes, loadMostRecentNote };
