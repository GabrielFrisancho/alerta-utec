export interface Incident {
  id: string;
  tipo: string;
  ubicacion: string;
  descripcion: string;
  urgencia: 'baja' | 'media' | 'alta' | 'critica';
  estado: 'pendiente' | 'en atencion' | 'resuelto';
  fecha: string;
  usuario: string;
}

export interface NewIncident {
  tipo: string;
  ubicacion: string;
  descripcion: string;
  urgencia: 'baja' | 'media' | 'alta' | 'critica';
}

export interface User {
  email: string;
  role: 'estudiante' | 'administrativo' | 'autoridad';
}