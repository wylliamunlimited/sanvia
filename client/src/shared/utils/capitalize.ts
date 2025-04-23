/**
 * Capitalizes the first letter of each word in a string
 * @param str The string to capitalize
 * @returns The string with first letter of each word capitalized
 */
export const capitalizeFirstLetter = (str: string): string => {
  return str.split(' ').map(word => 
    word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()
  ).join(' ');
}; 