import React, { useState, useEffect } from 'react';

const MedicationSearch = () => {
  const [medicationSearchTerm, setMedicationSearchTerm] = useState('');
  const [filteredMedications, setFilteredMedications] = useState<string[]>([]);
  const [medicationNames, setMedicationNames] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // Load and parse the file from public folder
  useEffect(() => {
    const fetchMedicationData = async () => {
      try {
        const response = await fetch('/RxTermsIngredients202504.txt');
        const text = await response.text();
        
        // Split the file by new lines, and then extract the medication names
        const names = text
          .split('\n')
          .map((line) => line.split('|')[1].trim()) // Get the medication name (second column)
          .filter((med) => med); // Remove any empty lines
        
        setMedicationNames(names);
        setIsLoading(false);
      } catch (error) {
        console.error('Error fetching the medication file:', error);
        setIsLoading(false);
      }
    };

    fetchMedicationData();
  }, []);

  // Handle search term change
  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setMedicationSearchTerm(value);

    // Filter the medications based on the search term
    const filtered = medicationNames.filter((med) =>
      med.toLowerCase().includes(value.toLowerCase())
    );
    setFilteredMedications(filtered.slice(0, 10)); // Limit to 10 results
  };

  return (
    <div>
      <input
        type="text"
        placeholder="Start typing a medication..."
        value={medicationSearchTerm}
        onChange={handleSearchChange}
        disabled={isLoading}
      />

      {isLoading && <div>Loading medications...</div>}

      {/* Show filtered results */}
      {medicationSearchTerm && filteredMedications.length > 0 && !isLoading && (
        <ul>
          {filteredMedications.map((med, index) => (
            <li key={index}>{med}</li>
          ))}
        </ul>
      )}

      {/* No results message */}
      {medicationSearchTerm && filteredMedications.length === 0 && !isLoading && (
        <div>No matching medications found</div>
      )}
    </div>
  );
};

export default MedicationSearch;
