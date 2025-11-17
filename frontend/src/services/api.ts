const API_BASE_URL = 'https://xxx.execute-api.us-east-1.amazonaws.com/dev';

export const api = {
  async createIncident(incident: any) {
    const response = await fetch(`${API_BASE_URL}/incidentes`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(incident)
    });
    return response.json();
  },

  async listIncidents() {
    const response = await fetch(`${API_BASE_URL}/incidentes`);
    const data = await response.json();
    return data.incidentes || [];
  },

  async getIncident(id: string) {
    const response = await fetch(`${API_BASE_URL}/incidentes/${id}`);
    const data = await response.json();
    return data.incidente;
  },

  async updateIncident(id: string, updates: any) {
    const response = await fetch(`${API_BASE_URL}/incidentes/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(updates)
    });
    return response.json();
  }
};