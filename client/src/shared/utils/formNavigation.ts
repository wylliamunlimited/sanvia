import { KeyboardEvent } from 'react';

/**
 * Handles form navigation by focusing on the next input field when the Enter key is pressed
 * @param e The KeyboardEvent object
 * @param nextField The type of the next input field to focus on
 * @param onSubmit The function to call when the Enter key is pressed
 */
export const handleFormNavigation = (
  e: KeyboardEvent<HTMLInputElement>,
  nextField?: string,
  onSubmit?: () => void
) => {
  if (e.key === 'Enter') {
    e.preventDefault();
    if (nextField) {
      const nextInput = document.querySelector(`input[type="${nextField}"]`) as HTMLInputElement;
      if (nextInput) {
        nextInput.focus();
      }
    } else if (onSubmit) {
      onSubmit();
    }
  }
}; 