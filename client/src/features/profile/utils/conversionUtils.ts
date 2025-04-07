export interface FeetInches {
  feet: number
  inches: number
}

export const cmToFeetInches = (cm: number) => {
  const totalInches = cm / 2.54
  const feet = Math.floor(totalInches / 12)
  const inches = Math.round(totalInches % 12)
  return { feet, inches }
}

export const feetInchesToCm = (feet: number, inches: number) => {
  return Math.round((feet * 12 + inches) * 2.54)
}

export const kgToLbs = (kg: number) => {
  return Math.round(kg * 2.20462)
}

export const lbsToKg = (lbs: number) => {
  return Math.round((lbs / 2.20462) * 10) / 10
}