"""Resumo sob demanda dos dados da ficha preventiva."""

from src.preventive_summary import accidents_text, annual_text, speed_text


def explain(card):
    location = card.localizacao
    sections = [
        ("Local e período", f"{card.titulo_curto}. {card.periodo}."),
        ("O que mais apareceu aqui", "\n\n".join(accidents_text(source) for source in card.dados["acidentes"])),
        ("Contagens de velocidade", speed_text(card.dados["trafego"], card.estado)),
        ("Ocorrências nos anos selecionados", annual_text(card.dados)),
        ("O que vale verificar agora", f"{card.proximo_passo} {card.motivo}"),
        ("Cobertura", card.cobertura),
        ("Registros por fonte", "\n\n".join(card.contexto)),
        ("Como o local foi identificado", f"{location['precisao']}. {location['motivo_localizacao']}"),
        ("O que ainda precisa ser confirmado", f"{card.falta} {card.responsavel}"),
    ]
    return "\n\n".join(f"**{label}.** {text}" for label, text in sections)


def render_explanation(card, version, query):
    import streamlit as st

    selection = (version, query, card)
    if st.button("Explique este trecho", key="explain_focus"):
        st.session_state["map_explanation"] = selection
    if st.session_state.get("map_explanation") == selection:
        st.caption("Resumo dos dados da ficha e dos critérios do painel.")
        st.markdown(explain(card))
