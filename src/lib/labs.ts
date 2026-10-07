/** Id de un lab a partir del id de su entrada en la colección (`<id>/index` → `<id>`). */
export function labIdOf(entryId: string): string {
  return entryId.replace(/\/index$/, '');
}
