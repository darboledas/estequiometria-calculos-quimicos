"""Pruebas independientes para la revisión científica de los capítulos 2 y 3.

Ejecutar desde la raíz del repositorio:
    python -m unittest discover -s pruebas_revision -v

Diseñadas sin librerías externas. Se incorporan sin sustituir las autopruebas
originales; constatan modelos, redondeos, entradas y casos de rechazo.
"""
from __future__ import annotations

import math
from decimal import Decimal
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "capitulo_02"))
sys.path.insert(0, str(ROOT / "capitulo_03"))

import unidades_y_dimensiones as ud  # noqa: E402
import ajuste_ecuaciones as ae  # noqa: E402
import conversion_rendimiento_selectividad as cr  # noqa: E402
import densidades_y_escalas as de  # noqa: E402
import masa_molar as mm  # noqa: E402
import reactivo_limitante as rl  # noqa: E402


class UnidadesEIncertidumbres(unittest.TestCase):
    def test_pulgada_a_metro(self):
        self.assertAlmostEqual(ud.convertir_unidad(1, "in", "m"), 0.0254)

    def test_pie_cubico_a_litros(self):
        self.assertAlmostEqual(ud.convertir_unidad(1, "ft3", "L"), 28.316846592)

    def test_concentracion_molar(self):
        self.assertEqual(ud.convertir_unidad(1, "mol/L", "mol/m3"), 1000)

    def test_centipoise(self):
        self.assertAlmostEqual(ud.convertir_unidad(1, "cP", "Pa·s"), 0.001)

    def test_conversion_incompatible_rechazada(self):
        with self.assertRaises(ValueError):
            ud.convertir_unidad(1, "kg", "mol")

    def test_celsius_a_kelvin(self):
        self.assertAlmostEqual(ud.convertir_temperatura(25, "°C", "K"), 298.15)

    def test_fahrenheit_a_celsius(self):
        self.assertAlmostEqual(ud.convertir_temperatura(32, "°F", "°C"), 0)

    def test_diferencia_termica_no_aplica_offset(self):
        self.assertAlmostEqual(ud.convertir_intervalo_temperatura(9, "°F", "K"), 5)

    def test_cero_absoluto(self):
        with self.assertRaises(ValueError):
            ud.convertir_temperatura(-274, "°C", "K")

    def test_cifras_significativas(self):
        self.assertEqual(ud.cifras_significativas_texto("0,00450"), 3)
        self.assertEqual(ud.cifras_significativas_texto("3,020e5"), 4)
        self.assertEqual(ud.cifras_significativas_texto("120,0"), 4)

    def test_notacion_incompleta_se_rechaza(self):
        for entrada in ("1e", "1eXYZ", "1e2e3"):
            with self.subTest(entrada=entrada), self.assertRaises(ValueError):
                ud.cifras_significativas_texto(entrada)

    def test_redondeo_al_par(self):
        self.assertEqual(ud.redondear_significativas("2,345", 3), Decimal("2.34"))
        self.assertEqual(ud.redondear_significativas("2,355", 3), Decimal("2.36"))

    def test_incertidumbre_no_correlacionada(self):
        u, _, _ = ud.propagar_incertidumbre_estandar([1, 1], [0.3, 0.4])
        self.assertAlmostEqual(u, 0.5)

    def test_correlacion_perfecta_positiva(self):
        u, _, _ = ud.propagar_incertidumbre_estandar(
            [1, 1], [0.3, 0.4], [[1, 1], [1, 1]]
        )
        self.assertAlmostEqual(u, 0.7)

    def test_correlacion_perfecta_negativa(self):
        u, _, _ = ud.propagar_incertidumbre_estandar(
            [1, 1], [0.3, 0.3], [[1, -1], [-1, 1]]
        )
        self.assertAlmostEqual(u, 0)

    def test_matriz_correlacion_no_psd(self):
        # Cada |r_ij| <= 1, simétrica y diagonal 1, pero autovalores negativos.
        # El código antiguo la aceptaba para c=(1,1,1) porque varianza=4,8>0.
        r = [[1, 0.9, 0.9], [0.9, 1, -0.9], [0.9, -0.9, 1]]
        with self.assertRaisesRegex(ValueError, "semidefinida positiva"):
            ud.propagar_incertidumbre_estandar([1, 1, 1], [1, 1, 1], r)

    def test_correlacion_simetrica_invalida(self):
        with self.assertRaises(ValueError):
            ud.matriz_covarianzas([1, 1], [[1, 0.8], [0.6, 1]])

    def test_reynolds_adimensional(self):
        rho = [1, -3, 0, 0, 0, 0, 0]
        v = [0, 1, -1, 0, 0, 0, 0]
        d = [0, 1, 0, 0, 0, 0, 0]
        mu = [1, -1, -1, 0, 0, 0, 0]
        resultado = ud.combinar_dimensiones(
            [rho, v, d, mu], [1, 1, 1, -1]
        )
        self.assertTrue(ud.es_adimensional(resultado))


class EcuacionesQuimicas(unittest.TestCase):
    def test_combustion_metano(self):
        self.assertEqual(ae.ajustar(["CH4", "O2"], ["CO2", "H2O"]), [1, 2, 1, 2])

    def test_combustion_etano(self):
        self.assertEqual(ae.ajustar(["C2H6", "O2"], ["CO2", "H2O"]), [2, 7, 4, 6])

    def test_neutralizacion(self):
        self.assertEqual(ae.ajustar(["Ca(OH)2", "HCl"], ["CaCl2", "H2O"]), [1, 2, 1, 2])

    def test_redox_carga(self):
        self.assertEqual(
            ae.ajustar(["MnO4^-", "H^+", "e^-"], ["Mn^2+", "H2O"]),
            [1, 8, 5, 1, 4],
        )

    def test_hidrato(self):
        self.assertEqual(ae.composicion("CuSO4·5H2O")[0],
                         {"Cu": 1, "S": 1, "O": 9, "H": 10})

    def test_coeficientes_erroneos(self):
        self.assertFalse(ae.comprobar(["H2", "O2"], ["H2O"], [1, 1, 1]))

    def test_reacciones_no_unicas(self):
        with self.assertRaisesRegex(ValueError, "no es único"):
            ae.ajustar(["C", "O2"], ["CO", "CO2"])


class ConversionYRendimiento(unittest.TestCase):
    def test_conversion(self):
        self.assertEqual(cr.fraccion_conversion(cr.Q(100), cr.Q(35)).v, Decimal("0.65"))

    def test_final_supera_inicial(self):
        with self.assertRaises(ValueError):
            cr.fraccion_conversion(cr.Q(10), cr.Q(11))

    def test_redondeo_de_entradas(self):
        self.assertEqual(cr.analizar_numero("12,30").p, -2)

    def test_rendimiento_global_en_etapas(self):
        self.assertEqual((cr.Q("0.9") * cr.Q("0.8") * cr.Q("0.75")).v,
                         Decimal("0.5400"))


class DensidadesYEscalas(unittest.TestCase):
    def test_brix_20(self):
        self.assertAlmostEqual(float(de.brix_a_ge(de.Q(20)).v),
                               1.08093 / 0.99821, places=5)

    def test_brix_inversa(self):
        ge = de.brix_a_ge(de.Q(20))
        self.assertAlmostEqual(float(de.ge_a_brix(ge).v), 20, places=9)

    def test_brix_fuera_de_tabla(self):
        with self.assertRaises(ValueError):
            de.brix_a_ge(de.Q(70))

    def test_api_35(self):
        valor = de.a_ge("7", de.Q("35"))
        self.assertAlmostEqual(float(valor.v), 141.5 / 166.5, places=12)

    def test_api_inversa(self):
        ge = de.a_ge("7", de.Q("35"))
        self.assertAlmostEqual(float(de.desde_ge("7", ge).v), 35, places=12)


class MasasMolares(unittest.TestCase):
    def test_agua(self):
        self.assertAlmostEqual(float(mm.calculate_molar_mass("H2O").raw_mass),
                               18.015, places=2)

    def test_sulfato_aluminio(self):
        self.assertAlmostEqual(float(mm.calculate_molar_mass("Al2(SO4)3").raw_mass),
                               342.13, places=2)

    def test_sulfato_cobre_pentahidratado(self):
        self.assertEqual(mm.calculate_molar_mass("CuSO4·5H2O").counts,
                         {"Cu": 1, "S": 1, "O": 9, "H": 10})

    def test_subindices_unicode(self):
        self.assertEqual(mm.calculate_molar_mass("H₂O").counts, {"H": 2, "O": 1})

    def test_elemento_desconocido(self):
        with self.assertRaises(ValueError):
            mm.calculate_molar_mass("Xx2")

    def test_grupo_vacio_se_rechaza(self):
        for formula in ("Fe()2", "Ca[]2", "Al{}2"):
            with self.subTest(formula=formula), self.assertRaisesRegex(ValueError, "vacíos"):
                mm.calculate_molar_mass(formula)


class ReactivoLimitante(unittest.TestCase):
    def test_limitante(self):
        resultado = rl.balance([rl.Q(5), rl.Q(2)], [2, 1], [2])
        self.assertEqual(resultado[1], [1])
        self.assertEqual(resultado[2].v, 2)
        self.assertEqual([r.v for r in resultado[4]], [1, 0])
        self.assertEqual([p.v for p in resultado[5]], [4])

    def test_conversion_parcial(self):
        resultado = rl.balance([rl.Q(2), rl.Q(1)], [2, 1], [2], rl.Q("0.5"))
        self.assertEqual([r.v for r in resultado[4]], [1, Decimal("0.5")])
        self.assertEqual([p.v for p in resultado[5]], [1])


class InterfazCLI(unittest.TestCase):
    def _ejecutar(self, ruta, *argumentos):
        return subprocess.run(
            [sys.executable, str(ROOT / ruta), *argumentos],
            cwd=ROOT, capture_output=True, text=True, timeout=12
        )

    def test_capitulo2_conversion_atm(self):
        p = self._ejecutar("capitulo_02/unidades_y_dimensiones.py", "convertir", "2,5", "atm", "Pa")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn("Pa", p.stdout)

    def test_capitulo2_rechaza_dimension_incompatible(self):
        p = self._ejecutar("capitulo_02/unidades_y_dimensiones.py", "convertir", "1", "kg", "s")
        self.assertEqual(p.returncode, 2)
        self.assertIn("No se puede convertir", p.stderr)

    def test_capitulo3_masa_molar_detalles(self):
        p = self._ejecutar("capitulo_03/masa_molar.py", "Al2(SO4)3", "--detalles")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn("342,13", p.stdout)

    def test_autopruebas_capitulos2y3(self):
        scripts = [
            ("capitulo_02/unidades_y_dimensiones.py", "--autocomprobar"),
            ("capitulo_03/ajuste_ecuaciones.py", "--autoprueba"),
            ("capitulo_03/conversion_rendimiento_selectividad.py", "--autoprueba"),
            ("capitulo_03/densidades_y_escalas.py", "--autoprueba"),
            ("capitulo_03/reactivo_limitante.py", "--autoprueba"),
        ]
        for ruta, opcion in scripts:
            with self.subTest(ruta=ruta):
                p = self._ejecutar(ruta, opcion)
                self.assertEqual(p.returncode, 0, p.stderr + p.stdout)


if __name__ == "__main__":
    unittest.main()
