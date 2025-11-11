# =============================================================
# 🦾 CONVERSOR DXF → TXT (versión modular para PyQt6)
# Harold & Abril · versión final estable
# =============================================================

import ezdxf
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import LineString, MultiLineString
from shapely.ops import linemerge, unary_union
from scipy.interpolate import splprep, splev
from sklearn.cluster import DBSCAN
from typing import List, Tuple, Optional
import os


class DXFProcessor:
    """Clase principal para procesar archivos DXF"""
    
    def __init__(self, tolerance: float = 0.05):
        self.tolerance = tolerance
        self.geoms = []
        self.merged_geoms = []
        self.centroids = None
        
    def load_dxf(self, dxf_path: str) -> bool:
        """Carga y procesa un archivo DXF"""
        try:
            doc = ezdxf.readfile(dxf_path)
            msp = doc.modelspace()
            self.geoms = []
            
            for entity in msp:
                self._process_entity(entity)
                
            if not self.geoms:
                raise ValueError("⚠️ No se detectaron entidades válidas en el DXF.")
                
            return True
            
        except Exception as e:
            raise Exception(f"❌ Error cargando DXF: {str(e)}")
    
    def _process_entity(self, entity) -> None:
        """Procesa una entidad individual del DXF"""
        dtype = entity.dxftype()
        puntos = []
        
        try:
            if dtype == "LINE":
                start, end = entity.dxf.start, entity.dxf.end
                puntos = [[start.x, start.y], [end.x, end.y]]

            elif dtype == "LWPOLYLINE":
                pts = np.array(entity.get_points())[:, :2]
                puntos = pts

            elif dtype == "POLYLINE":
                pts = [v.dxf.location[:2] for v in entity.vertices]
                puntos = np.array(pts)

            elif dtype == "CIRCLE":
                c, r = entity.dxf.center, entity.dxf.radius
                t = np.linspace(0, 2*np.pi, 200)
                puntos = np.column_stack([c.x + r*np.cos(t), c.y + r*np.sin(t)])

            elif dtype == "ARC":
                c, r = entity.dxf.center, entity.dxf.radius
                a1, a2 = np.deg2rad(entity.dxf.start_angle), np.deg2rad(entity.dxf.end_angle)
                t = np.linspace(a1, a2, 120)
                puntos = np.column_stack([c.x + r*np.cos(t), c.y + r*np.sin(t)])

            elif dtype == "SPLINE":
                puntos = self._process_spline(entity)

            if len(puntos) > 1:
                self.geoms.append(LineString(puntos))

        except Exception as ex:
            print(f"⚠️ No se pudo procesar {dtype}: {ex}")
    
    def _process_spline(self, spline_entity) -> np.ndarray:
        """Procesa entidades SPLINE"""
        fit = np.array(spline_entity.fit_points)
        if len(fit) >= 2:
            tck, _ = splprep([fit[:,0], fit[:,1]], s=0)
            u = np.linspace(0, 1, 200)
            x, y = splev(u, tck)
            return np.column_stack([x, y])
        else:
            ctrl = np.array(spline_entity.control_points)
            if len(ctrl) >= 2:
                tck, _ = splprep([ctrl[:,0], ctrl[:,1]], s=0)
                u = np.linspace(0, 1, 200)
                x, y = splev(u, tck)
                return np.column_stack([x, y])
        return np.array([])
    
    def cluster_endpoints(self) -> None:
        """Agrupa endpoints usando DBSCAN"""
        if not self.geoms:
            raise ValueError("No hay geometrías para procesar")
            
        endpoints = []
        endpoint_map = []
        
        for gi, g in enumerate(self.geoms):
            coords = list(g.coords)
            endpoints.append(coords[0])
            endpoint_map.append((gi, 0))
            endpoints.append(coords[-1])
            endpoint_map.append((gi, -1))

        endpoints = np.array(endpoints)
        clustering = DBSCAN(eps=self.tolerance, min_samples=1, metric='euclidean')
        labels = clustering.fit_predict(endpoints)
        n_clusters = labels.max() + 1
        
        # Calcular centroides
        self.centroids = np.zeros((n_clusters, 2))
        for k in range(n_clusters):
            pts = endpoints[labels == k]
            self.centroids[k] = pts.mean(axis=0)
        
        # Reemplazar extremos por centroides
        geoms_sanitized = []
        for gi, g in enumerate(self.geoms):
            coords = list(g.coords)
            label_start = labels[2*gi]
            label_end = labels[2*gi + 1]
            new_coords = coords.copy()
            new_coords[0] = tuple(self.centroids[label_start])
            new_coords[-1] = tuple(self.centroids[label_end])
            geoms_sanitized.append(LineString(new_coords))
            
        self.geoms = geoms_sanitized
    
    def merge_geometries(self) -> None:
        """Une líneas conectadas"""
        if not self.geoms:
            raise ValueError("No hay geometrías para fusionar")
            
        union = unary_union(self.geoms)
        merged = linemerge(union)

        if isinstance(merged, LineString):
            self.merged_geoms = [merged]
        elif isinstance(merged, MultiLineString):
            self.merged_geoms = list(merged.geoms)
        else:
            self.merged_geoms = []
    
    def process_file(self, dxf_path: str) -> bool:
        """Procesa completo del archivo DXF"""
        try:
            # 1. Cargar DXF
            if not self.load_dxf(dxf_path):
                return False
                
            # 2. Agrupar endpoints
            self.cluster_endpoints()
            
            # 3. Unir geometrías
            self.merge_geometries()
            
            return True
            
        except Exception as e:
            raise Exception(f"Error en procesamiento: {str(e)}")
    
    def get_statistics(self) -> dict:
        """Retorna estadísticas del procesamiento"""
        return {
            'original_entities': len(self.geoms),
            'final_trajectories': len(self.merged_geoms),
            'tolerance_used': self.tolerance
        }
    
    def export_to_txt(self, output_path: str) -> str:
        """Exporta las trayectorias a archivo TXT"""
        if not self.merged_geoms:
            raise ValueError("No hay trayectorias para exportar")
            
        with open(output_path, 'w') as f:
            f.write("X Y\n")
            for geom in self.merged_geoms:
                x, y = geom.xy
                for xi, yi in zip(x, y):
                    f.write(f"{xi:.6f} {yi:.6f}\n")
                f.write("NaN NaN\n")
        
        return output_path
    
    def plot_result(self, save_path: Optional[str] = None) -> None:
        """Genera gráfico de las trayectorias resultantes"""
        if not self.merged_geoms:
            raise ValueError("No hay trayectorias para graficar")
            
        plt.figure(figsize=(8, 8))
        for i, geom in enumerate(self.merged_geoms):
            x, y = geom.xy
            plt.plot(x, y, linewidth=1.2, label=f"Trayectoria {i+1}")
        
        plt.axis('equal')
        plt.title("🧩 Figura reconstruida (DBSCAN robusto)")
        plt.xlabel("X [mm]")
        plt.ylabel("Y [mm]")
        plt.grid(True)
        plt.legend()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()


# =============================================================
# EJEMPLO DE USO (para testing)
# =============================================================
def main():
    """Función principal para testing"""
    # Crear procesador
    processor = DXFProcessor(tolerance=0.05)
    
    try:
        # Procesar archivo (ejemplo - necesitarías un archivo real)
        success = processor.process_file("tu_archivo.dxf")
        
        # Si tuvieras un archivo, descomenta:
        if success:
            stats = processor.get_statistics()
            print(f" Procesamiento completado:")
            print(f"   - Entidades originales: {stats['original_entities']}")
            print(f"   - Trayectorias finales: {stats['final_trajectories']}")
            
            # Exportar
            output_file = processor.export_to_txt("trayectoria_XY_robusta.txt")
            print(f" Archivo exportado: {output_file}")
            
            # Graficar
            processor.plot_result()
        
        print(" Módulo DXFProcessor cargado correctamente")
        print(" Listo para integrar con PyQt6")
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()