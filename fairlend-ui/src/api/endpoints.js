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
export async function runAudit(sessionId, protectedCol, targetCol) {
  const { data } = await apiClient.post('/audit', {
    session_id: sessionId,
    protected_column: protectedCol,
    target_column: targetCol,
  });
  return data;
}
export async function runDebias(sessionId, fairnessWeight, protectedCol, targetCol) {
  const { data } = await apiClient.post('/debias', {
    session_id: sessionId,
    fairness_weight: fairnessWeight,
    protected_column: protectedCol,
    target_column: targetCol,
  });
  return data;
}