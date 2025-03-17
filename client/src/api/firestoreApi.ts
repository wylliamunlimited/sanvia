import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const TEST_AUTH_TOKEN = import.meta.env.VITE_TEST_AUTH_TOKEN;  // Testing

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
    uploadSurvey: async (age: string, gender: string, sex: string, height: string, weight: string): Promise<any> => {
        try {
            const response = await api.post<any>('/survey', { 
                "age": age,
                "gender": gender,
                "sex": sex,
                "height": height,
                "weight": weight
            });
            return response.data;
        } catch (error) {
            console.error('Error uploading survey data:', error);
            throw error;
        }
    },
    uploadNames: async (first_name: string, last_name: string): Promise<any> => {
        try {
            const response = await api.post<any>(`/store-names?first_name=${first_name}&last_name=${last_name}`, {});
            return response.data;
        } catch (error) {
            console.error('Error uploading names:', error);
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
    }
};