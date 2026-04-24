import { apiClient } from './client';

export async function uploadDataset(file) {
  const formData = new FormData();
  formData.append('file', file);
  
  const { data } = await apiClient.post('/upload', formData, {
    headers: { 
      'Content-Type': 'multipart/form-data' 
    }
  });
  return data;
}