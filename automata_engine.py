"""
Módulo de Autómatas para el Juego de la Memoria (Memotest)
Fundamentos Teóricos de Informática - Grupo N°2 (2026)
Integrantes: Alexis Mariqueo, Cesar Millavanque, Daniel Enegron, Kadir Martinez

Este módulo define formalmente:
1. Autómata Finito Determinista (AFD) completo para el progreso de la partida.
2. Autómata de Pila Determinista (AP / DPDA) para el control de errores y vidas.
"""

from typing import Dict, List, Optional, Set, Tuple
from automata.fa.dfa import DFA
from automata.pda.dpda import DPDA
from automata.base.exceptions import RejectionException


def build_progress_dfa(pairs_count: int) -> DFA:
    """
    Construye el AFD completo según la especificación del informe:
    - Alfabeto: Σ = {a, e, x}
      * 'a': Acierto (par coincidente encontrado)
      * 'e': Error (par no coincidente)
      * 'x': Jugada inválida (carta ya volteada o acción no permitida)
    - Estados: {q0, q1, ..., qN, q_sumidero} donde N es pairs_count (4 en fácil, 8 en difícil).
    - Estado Inicial: q0
    - Estados Finales: {qN}
    - Transiciones:
      * q_i --'a'--> q_{i+1} (para i de 0 a N-1)
      * q_i --'e'--> q_i
      * q_i --'x'--> q_i
      * qN --{a, e, x}--> q_sumidero
      * q_sumidero --{a, e, x}--> q_sumidero
    """
    states: Set[str] = {f"q{i}" for i in range(pairs_count + 1)} | {"q_sumidero"}
    input_symbols: Set[str] = {"a", "e", "x"}
    transitions: Dict[str, Dict[str, str]] = {}

    for i in range(pairs_count):
        transitions[f"q{i}"] = {
            "a": f"q{i+1}",
            "e": f"q{i}",
            "x": f"q{i}"
        }

    # Estado final qN y q_sumidero van a q_sumidero ante cualquier símbolo posterior
    final_state = f"q{pairs_count}"
    transitions[final_state] = {
        "a": "q_sumidero",
        "e": "q_sumidero",
        "x": "q_sumidero"
    }
    transitions["q_sumidero"] = {
        "a": "q_sumidero",
        "e": "q_sumidero",
        "x": "q_sumidero"
    }

    return DFA(
        states=states,
        input_symbols=input_symbols,
        transitions=transitions,
        initial_state="q0",
        final_states={final_state}
    )


def build_lives_pda() -> DPDA:
    """
    Construye el Autómata de Pila Determinista (DPDA) según la especificación del informe:
    - Q (Estados): {q0, q1, q2}
    - ΣE (Alfabeto de entrada): {a, e, x}
    - ΣP (Alfabeto de la pila): {Z, V} (Z = fondo de pila, V = vida)
    - Estado Inicial: q0
    - Símbolo Inicial de Pila: Z
    - Estados Finales: {q2}
    - Condición de Aceptación: Por pila vacía (acceptance_mode='empty_stack')
    
    Transiciones:
    - (q0, λ, Z) -> (q1, VVVVVZ)   [Carga inicial de 5 vidas manteniendo Z al fondo]
    - (q1, a, V) -> (q1, V)        [Acierto: desapila V y vuelve a apilar V, vidas intactas]
    - (q1, x, V) -> (q1, V)        [Inválido: desapila V y vuelve a apilar V, vidas intactas]
    - (q1, e, V) -> (q1, λ)        [Error: desapila V y no apila nada, consume 1 vida]
    - (q1, λ, Z) -> (q2, λ)        [Al consumir 5 vidas, tope es Z; por λ pasa a q2 vaciando la pila -> DERROTA]
    """
    return DPDA(
        states={"q0", "q1", "q2"},
        input_symbols={"a", "e", "x"},
        stack_symbols={"Z", "V"},
        transitions={
            "q0": {
                "": {
                    "Z": ("q1", ("V", "V", "V", "V", "V", "Z"))
                }
            },
            "q1": {
                "a": {"V": ("q1", ("V",))},
                "x": {"V": ("q1", ("V",))},
                "e": {"V": ("q1", "")},
                "": {"Z": ("q2", "")}
            },
            "q2": {}
        },
        initial_state="q0",
        initial_stack_symbol="Z",
        final_states={"q2"},
        acceptance_mode="empty_stack"
    )


class AutomataGameController:
    """
    Controlador en tiempo real que ejecuta el AFD de progreso y el AP de vidas.
    Mantiene la sincronía entre el juego interactivo y los modelos teóricos de automata-lib.
    """

    def __init__(self, pairs_count: int = 4):
        self.pairs_count = pairs_count
        self.dfa = build_progress_dfa(pairs_count)
        self.pda = build_lives_pda()
        self.reset(pairs_count)

    def reset(self, pairs_count: Optional[int] = None):
        """Reinicia los autómatas a su estado inicial."""
        if pairs_count is not None:
            self.pairs_count = pairs_count
            self.dfa = build_progress_dfa(pairs_count)

        self.word_history: str = ""
        self.dfa_state: str = "q0"
        self.dfa_history: List[str] = ["q0"]
        
        # Estado inicial del AP tras transición lambda inicial (q0 -> q1 con 5 V y Z)
        self.pda_state: str = "q1"
        self.pda_stack: List[str] = ["Z", "V", "V", "V", "V", "V"]
        self.pda_history: List[Tuple[str, List[str]]] = [("q1", list(self.pda_stack))]
        
        self.is_victory: bool = False
        self.is_defeat_by_errors: bool = False
        self.last_transition_dfa: str = "q0 (Inicio)"
        self.last_transition_pda: str = "λ, Z ; VVVVVZ"
        self.last_symbol: Optional[str] = None

    def step(self, symbol: str) -> dict:
        """
        Procesa un símbolo del alfabeto Σ = {'a', 'e', 'x'}.
        Retorna un diccionario con los detalles de la transición en ambos autómatas.
        """
        if symbol not in {"a", "e", "x"}:
            raise ValueError(f"Símbolo '{symbol}' no pertenece al alfabeto Σ = {{a, e, x}}")

        self.last_symbol = symbol
        prev_dfa = self.dfa_state
        prev_pda = self.pda_state
        prev_stack = list(self.pda_stack)

        # 1. Procesar símbolo en el AFD de progreso
        next_dfa = self.dfa.transitions[self.dfa_state][symbol]
        self.dfa_state = next_dfa
        self.dfa_history.append(self.dfa_state)
        self.last_transition_dfa = f"δ({prev_dfa}, {symbol}) = {next_dfa}"

        # Comprobar si llegó al estado final de victoria
        if self.dfa_state in self.dfa.final_states:
            self.is_victory = True

        # 2. Procesar símbolo en el AP de vidas
        self.word_history += symbol
        configs = []
        accepted = False
        try:
            for cfg in self.pda.read_input_stepwise(self.word_history):
                configs.append(cfg)
            accepted = True
        except RejectionException:
            accepted = False

        if configs:
            last_cfg = configs[-1]
            self.pda_state = last_cfg.state
            self.pda_stack = list(last_cfg.stack)
            self.pda_history.append((self.pda_state, list(self.pda_stack)))

        # Descripción de la transición realizada en el AP
        if symbol == "a":
            self.last_transition_pda = f"({prev_pda}, a, V) -> ({self.pda_state}, V)"
        elif symbol == "x":
            self.last_transition_pda = f"({prev_pda}, x, V) -> ({self.pda_state}, V)"
        elif symbol == "e":
            if accepted:
                self.last_transition_pda = f"({prev_pda}, e, V) -> (q1, λ) -> λ, Z;λ -> (q2, λ)"
            else:
                self.last_transition_pda = f"({prev_pda}, e, V) -> ({self.pda_state}, λ)"

        if accepted:
            self.is_defeat_by_errors = True

        return {
            "symbol": symbol,
            "dfa_state": self.dfa_state,
            "dfa_accepted": self.is_victory,
            "pda_state": self.pda_state,
            "pda_stack": list(self.pda_stack),
            "lives": self.lives,
            "pda_accepted_empty_stack": self.is_defeat_by_errors,
            "dfa_transition": self.last_transition_dfa,
            "pda_transition": self.last_transition_pda
        }

    @property
    def lives(self) -> int:
        """Cantidad de vidas restantes según los símbolos 'V' presentes en la pila."""
        return self.pda_stack.count("V")

    @property
    def pairs_found(self) -> int:
        """Pares descubiertos según el estado del AFD (q_i -> i aciertos)."""
        if self.dfa_state == "q_sumidero":
            return self.pairs_count
        try:
            return int(self.dfa_state.replace("q", ""))
        except ValueError:
            return 0

