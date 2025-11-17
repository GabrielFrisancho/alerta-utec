import React from 'react';
import { Incident } from '../models/types';

interface IncidentListProps {
  incidentes: Incident[];
}

const IncidentList: React.FC<IncidentListProps> = ({ incidentes }) => {
  const getUrgencyColor = (urgencia: string): string => {
    switch (urgencia) {
      case 'critica': return '#dc3545';
      case 'alta': return '#fd7e14';
      case 'media': return '#ffc107';
      case 'baja': return '#28a745';
      default: return '#6c757d';
    }
  };

  const getStatusColor = (estado: string): string => {
    switch (estado) {
      case 'pendiente': return '#6c757d';
      case 'en atencion': return '#007bff';
      case 'resuelto': return '#28a745';
      default: return '#6c757d';
    }
  };

  return (
    <div className="lista-incidentes">
      <h2>Incidentes Activos ({incidentes.length})</h2>
      
      {incidentes.length === 0 ? (
        <p className="no-incidents">No hay incidentes activos</p>
      ) : (
        <div className="incidentes-grid">
          {incidentes.map(inc => (
            <div key={inc.id} className="incidente-card">
              <div 
                className="urgency-bar"
                style={{ backgroundColor: getUrgencyColor(inc.urgencia) }}
              ></div>
              
              <div className="card-content">
                <div className="card-header">
                  <h3>{inc.tipo}</h3>
                  <span 
                    className="urgency-badge"
                    style={{ backgroundColor: getUrgencyColor(inc.urgencia) }}
                  >
                    {inc.urgencia}
                  </span>
                </div>
                
                <p className="location">📍 {inc.ubicacion || 'Ubicación no especificada'}</p>
                <p className="description">{inc.descripcion}</p>
                
                <div className="card-footer">
                  <span 
                    className="status-badge"
                    style={{ backgroundColor: getStatusColor(inc.estado) }}
                  >
                    {inc.estado}
                  </span>
                  <span className="date">
                    {new Date(inc.fecha).toLocaleDateString('es-PE', {
                      hour: '2-digit',
                      minute: '2-digit'
                    })}
                  </span>
                </div>
                
                <small className="reporter">Reportado por: {inc.usuario}</small>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default IncidentList;