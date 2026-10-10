# clean-architecture-pos-fallback 🏗️💳

[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Live%20Showcase-amber?style=for-the-badge&logo=github)](https://alejano.github.io/clean-architecture-pos-fallback/)
[![Kotlin](https://img.shields.io/badge/Kotlin-1.9.22-purple?style=for-the-badge&logo=kotlin)](https://kotlinlang.org)
[![Python](https://img.shields.io/badge/Python-3.12%2B-blue?style=for-the-badge&logo=python)](https://python.org)

**Autor:** Alejandro Barragán Jasso  
**Enfoque:** Tech Lead / Mobile & Embedded Payment Systems Engineer

> 🌐 **Página Web Interactiva:** Visita las diapositivas interactivas y prueba el simulador de la máquina de estados con Fallback en [alejano.github.io/clean-architecture-pos-fallback](https://alejano.github.io/clean-architecture-pos-fallback/).

---

## 🎯 Objetivo de la Publicación

Migración de librerías transaccionales en Android hacia Clean Architecture y Kotlin moderno para eliminar memory leaks en corrutinas al interactuar con hardware físico (sensores de chip, cabezales magnéticos).

Puntos destacados:
1. **Eliminación de Coroutine Leaks:** Sustitución de `CoroutineScope(Dispatchers.IO)` sin ciclo de vida por flujos atómicos en casos de uso.
2. **Máquina de Estados Finita Determinista:** Activación del modo de contingencia (*Fallback a banda magnética*) estrictamente tras **3 intentos fallidos consecutivos de chip**.
3. **Desacoplamiento de Pantalla Dual:** La pantalla del cliente no ejecuta lógica; se sincroniza vía bus reactivo de eventos.
4. **Métricas:** 0 fugas de memoria en pruebas de estrés y >70% de cobertura en tests unitarios.

---

## 🚀 Cómo Probar el Código

```bash
python payment_state_machine.py
```

---

## 📱 Publicación en LinkedIn
El texto para LinkedIn y el guión del carrusel están en [POST_LINKEDIN.md](POST_LINKEDIN.md).
