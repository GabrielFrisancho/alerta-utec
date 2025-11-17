import React, { useState } from 'react';
import { NewIncident } from '../models/types';

interface IncidentFormProps {
  onReport: (incident: NewIncident) => void;
}

const IncidentForm: React.FC<IncidentFormProps> = ({ onReport }) => {
  const [nuevoIncidente, setNuevoIncidente] = useState<NewIncident>({
    tipo: '',
    ubicacion: '',
    descripcion: '',
    urgencia: 'media'
  });

  const tiposIncidente: string[] = [
    'Infraestructura',
    'Seguridad',
    'Salud',
    'Servicios',
    'Académico',
    'Otro'
  ];

  const handleSubmit = (e: React.FormEvent): void => {
    e.preventDefault();
    if (nuevoIncidente.tipo && nuevoIncidente.descripcion) {
      onReport(nuevoIncidente);
      setNuevoIncidente({
        tipo: '',
        ubicacion: '',
        descripcion: '',
        urgencia: 'media'
      });
    } else {
      alert('Por favor complete los campos obligatorios');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="reporte-form">
      <h2>Reportar Incidente</h2>
      
      <div className="form-group">
        <label>Tipo de Incidente *</label>
        <select 
          value={nuevoIncidente.tipo}
          onChange={(e) => setNuevoIncidente({
            ...nuevoIncidente, 
            tipo: e.target.value
          })}
          required
        >
          <option value="">Seleccione tipo</option>
          {tiposIncidente.map(tipo => (
            <option key={tipo} value={tipo}>{tipo}</option>
          ))}
        </select>
      </div>

      <div className="form-group">
        <label>Ubicación</label>
        <input 
          type="text"
          placeholder="Ej: Edificio A, Aula 301"
          value={nuevoIncidente.ubicacion}
          onChange={(e) => setNuevoIncidente({
            ...nuevoIncidente, 
            ubicacion: e.target.value
          })}
        />
      </div>

      <div className="form-group">
        <label>Descripción *</label>
        <textarea 
          placeholder="Describa el incidente en detalle..."
          value={nuevoIncidente.descripcion}
          onChange={(e) => setNuevoIncidente({
            ...nuevoIncidente, 
            descripcion: e.target.value
          })}
          required
          rows={4}
        />
      </div>

      <div className="form-group">
        <label>Nivel de Urgencia</label>
        <select 
          value={nuevoIncidente.urgencia}
          onChange={(e) => setNuevoIncidente({
            ...nuevoIncidente, 
            urgencia: e.target.value as NewIncident['urgencia']
          })}
        >
          <option value="baja">Baja</option>
          <option value="media">Media</option>
          <option value="alta">Alta</option>
          <option value="critica">Crítica</option>
        </select>
      </div>

      <button type="submit" className="submit-btn">
        🚨 Reportar Incidente
      </button>
    </form>
  );
};

export default IncidentForm;