import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
// const TEST_AUTH_TOKEN = import.meta.env.VITE_TEST_AUTH_TOKEN;  // Testing

export enum Gender {
    Men = "Men",
    Women = "Women",
    Nonbinary = "Nonbinary"
}

export enum Sex {
    Male = "Male",
    Female = "Female",
    Intersex = "Intersex"
}

// export interface SurveyEntry {
//     age: number;
//     gender: Gender;
//     sex: Sex;
//     height: number;
//     weight: number;
// }

const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json'
    }
});

api.interceptors.request.use((config) => {
    const token = localStorage.getItem('sanvia-refreshToken');
    if (token) {
        config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
});

export const firestoreApi = {
    initializeProfile: async (first_name: string, last_name: string): Promise<any> => {
        try {
            const response = await api.post<any>('/initialize-profile', {
                first_name: first_name,
                last_name: last_name
            });
            return response.data;
        } catch (error) {
            console.error('Error initializing profile:', error);
            throw error;
        }
    },
    
    get_user_profile: async (): Promise<any> => {
        try {
            const response = await api.get<any>(`/get-profile`);
            console.log(response.data);
            return response.data;
        } catch (error) {
            console.error('Error retrieving profile data:', error);
        }
    },

    updateProfile: async (firstName: string, lastName: string, age: string, gender: string, sex: string, height: string, weight: string, conditions: string[], medications: string[]): Promise<any> => {
        try {
            const response = await api.post<any>('/update-profile', { 
                "first_name": firstName,
                "last_name": lastName,
                "age": age,
                "gender": gender,
                "sex": sex,
                "height": height,
                "weight": weight,
                "conditions": conditions,
                "medications": medications
            });
            return response.data;
        } catch (error) {
            console.error('Error updating profile data:', error);
            throw error;
        }
    },

    deleteUserData: async (): Promise<any> => {
        try {
            const response = await api.post<any>('/delete-user-data/delete-user-data');
            return response.data;
        } catch (error) {
            console.error('Error deleting user data:', error);
            throw error;
        }
    },

    deleteAccount: async (): Promise<any> => {
        try {
            const response = await api.post<any>('/delete-user-data/delete-account');
            return response.data;
        } catch (error) {
            console.error('Error deleting account:', error);
            throw error;
        }
    },

    deleteAllChats: async (): Promise<any> => {
        try {
            const response = await api.post<any>('/delete-user-data/delete-all-chats');
            return response.data;
        } catch (error) {
            console.error('Error deleting all chats:', error);
            throw error;
        }
    },

    deleteDocument: async (documentId: string): Promise<any> => {
        try {
            const response = await api.post<any>(`/delete-user-data/delete-document/${documentId}`);
            return response.data;
        } catch (error) {
            console.error('Error deleting document:', error);
            throw error;
        }
    }
};