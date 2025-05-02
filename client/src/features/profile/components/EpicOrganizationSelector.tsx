import React, { useState, useEffect } from 'react';
import './EpicOrganizationSelector.css';

interface Organization {
    id: string;
    name: string;
    endpoint: string;
}

interface EpicOrganizationSelectorProps {
    onSelect: (endpoint: string) => void;
    onClose: () => void;
}

const EpicOrganizationSelector: React.FC<EpicOrganizationSelectorProps> = ({ onSelect, onClose }) => {
    const [organizations, setOrganizations] = useState<Organization[]>([]);
    const [searchTerm, setSearchTerm] = useState('');
    const [loading, setLoading] = useState(true);



    useEffect(() => {
        const fetchOrganizations = async () => {
            try {
                const response = await fetch('/user-access-brands-endpoint-bundle.json');
                const data = await response.json();

                const orgs = data.entry
                    .filter((entry: any) => entry.resource.resourceType === 'Organization')
                    .map((orgEntry: any) => {
                        // Get the endpoint reference if it exists
                        const endpointRef = orgEntry.resource.endpoint?.[0]?.reference;
                        let endpoint = '';

                        if (endpointRef) {
                            const endpointEntry = data.entry.find(
                                (entry: any) =>
                                    entry.resource.resourceType === 'Endpoint' &&
                                    entry.fullUrl === endpointRef
                            );
                            endpoint = endpointEntry?.resource.address || '';
                        }

                        return {
                            id: orgEntry.resource.id,
                            name: orgEntry.resource.name,
                            endpoint: endpoint
                        };
                    })
                    .filter((org: Organization) => org.endpoint); // Only include organizations with valid endpoints

                // Add EPIC test environment at the beginning of the list
                const allOrgs = [
                    {
                        id: 'epic-test',
                        name: 'EPIC Test Environment',
                        endpoint: 'https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4/'
                    },
                    ...orgs
                ];

                setOrganizations(allOrgs);
            } catch (error) {
                console.error('Error fetching organizations:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchOrganizations();
    }, []);

    const filteredOrganizations = organizations.filter(org =>
        org.name.toLowerCase().includes(searchTerm.toLowerCase())
    );

    return (
        <>
            <div className="epic-selector-overlay" onClick={onClose} />
            <div className="epic-selector-popup">
                <div className="epic-selector-content">
                    <div className="epic-selector-header">
                        <h3>Select Your Healthcare Organization</h3>
                        <button className="close-button" onClick={onClose}>×</button>
                    </div>

                    <div className="search-container">
                        <input
                            type="text"
                            placeholder="Search organizations..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            className="search-input"
                        />
                    </div>

                    <div className="organizations-list">
                        {loading ? (
                            <div className="loading">Loading organizations...</div>
                        ) : filteredOrganizations.length === 0 ? (
                            <div className="no-results">No organizations found</div>
                        ) : (
                            filteredOrganizations.map((org) => (
                                <div
                                    key={org.id}
                                    className="organization-item"
                                    onClick={() => onSelect(org.endpoint)}
                                >
                                    {org.name}
                                </div>
                            ))
                        )}
                    </div>
                </div>
            </div>
        </>
    );
};

export default EpicOrganizationSelector; 