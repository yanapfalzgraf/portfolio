"""Kontaktformular und schwebender Portfolio-Chatbot für Streamlit."""

from __future__ import annotations

import html
import re
import smtplib
from email.message import EmailMessage

import streamlit as st


_INITIAL_MESSAGE = (
    "Hallo! Ich bin Yanas Portfolio-Assistent. "
    "Ich beantworte Fragen zu ihren Projekten, ihrer Erfahrung, "
    "ihren Kompetenzen und ihrer Arbeitsweise."
)

_EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def init_chat_state() -> None:
    """Initialisiert Kontaktformular und Chat-Zustand."""
    st.session_state.setdefault("contact_form_open", False)
    st.session_state.setdefault(
        "portfolio_chat_messages",
        [{"role": "assistant", "content": _INITIAL_MESSAGE}],
    )


def create_chat_response(question: str) -> str:
    """Erzeugt kontrollierte Antworten zum Portfolio."""
    normalized = " ".join(question.lower().split())

    if any(term in normalized for term in ("hallo", "hello", "hi", "guten tag", "hey")):
        return (
            "Hallo! Schön, dass du da bist. "
            "Du kannst mich zu Yanas Projekten, UX-Erfahrung, "
            "Data-Analytics-Skills oder Kontaktmöglichkeiten fragen."
        )

    if any(term in normalized for term in ("projekt", "projekte", "portfolio")):
        return (
            "Yanas Portfolio verbindet UX/UI- und Product-Design-Erfahrung "
            "mit Data Analytics und Data Science. Dazu gehören Projekte für "
            "Murrelektronik, OPTIMA, MeaPuna und Mercedes-Benz sowie "
            "Analytics-Projekte mit Power BI, Python und Streamlit."
        )

    if any(term in normalized for term in ("erfahrung", "beruf", "senior", "ux", "ui")):
        return (
            "Yana bringt mehr als zehn Jahre Erfahrung in UX/UI Design "
            "und der Entwicklung digitaler Produkte mit. Heute verbindet sie "
            "diese Erfahrung mit moderner Datenanalyse und produktorientiertem Denken."
        )

    if any(
        term in normalized
        for term in (
            "python",
            "sql",
            "power bi",
            "pandas",
            "data",
            "daten",
            "skill",
            "kompetenz",
            "machine learning",
        )
    ):
        return (
            "Zu Yanas Kompetenzen gehören Python, Pandas, SQL, Excel, Power BI, "
            "Datenvisualisierung, explorative Analyse, Statistik und Machine Learning. "
            "Hinzu kommen UX Research, UI Design, Prototyping und Stakeholder-Kommunikation."
        )

    if any(term in normalized for term in ("end-to-end", "arbeitsweise", "prozess", "ansatz")):
        return (
            "Ihr Ansatz ist End-to-End und nutzerzentriert: "
            "Verstehen, Analysieren, Insights ableiten, Entscheiden "
            "sowie Maßnahmen umsetzen und optimieren."
        )

    if any(term in normalized for term in ("kontakt", "email", "e-mail", "erreichen", "nachricht")):
        return (
            "Nutze bitte den Button „Kontakt aufnehmen“ im Kontaktbereich. "
            "Dort kannst du Yana über ein separates Formular direkt eine Nachricht senden."
        )

    if any(term in normalized for term in ("standort", "ort", "gaildorf")):
        return "Yana ist in Gaildorf, Deutschland, ansässig."

    return (
        "Dazu habe ich aktuell keine spezifische Portfolio-Antwort. "
        "Am besten fragst du mich nach Projekten, Erfahrung, Skills, "
        "Arbeitsweise oder Kontaktmöglichkeiten."
    )


def _required_secret(name: str) -> str:
    value = st.secrets.get(name)
    if value is None or str(value).strip() == "":
        raise KeyError(name)
    return str(value).strip()


def send_contact_email(
    *,
    name: str,
    sender_email: str,
    company: str,
    message: str,
) -> tuple[bool, str]:
    """Sendet eine Kontaktanfrage per SMTP."""
    try:
        smtp_host = _required_secret("SMTP_HOST")
        smtp_port = int(_required_secret("SMTP_PORT"))
        smtp_user = _required_secret("SMTP_USER")
        smtp_password = _required_secret("SMTP_PASSWORD")
        contact_email = _required_secret("CONTACT_EMAIL")

        use_ssl = bool(st.secrets.get("SMTP_USE_SSL", False))
        use_starttls = bool(st.secrets.get("SMTP_USE_STARTTLS", not use_ssl))

        mail = EmailMessage()
        mail["Subject"] = f"Neue Portfolio-Anfrage von {name}"
        mail["From"] = smtp_user
        mail["To"] = contact_email
        mail["Reply-To"] = sender_email
        mail.set_content(
            f"""
Neue Kontaktanfrage über das Portfolio

Name: {name}
E-Mail: {sender_email}
Unternehmen: {company or "Nicht angegeben"}

Nachricht:
{message}
""".strip()
        )

        if use_ssl:
            with smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=20) as server:
                server.login(smtp_user, smtp_password)
                server.send_message(mail)
        else:
            with smtplib.SMTP(smtp_host, smtp_port, timeout=20) as server:
                server.ehlo()
                if use_starttls:
                    server.starttls()
                    server.ehlo()
                server.login(smtp_user, smtp_password)
                server.send_message(mail)

        return True, (
            "Vielen Dank! Deine Nachricht wurde erfolgreich an Yana gesendet. "
            "Sie kann dir direkt an die angegebene E-Mail-Adresse antworten."
        )

    except KeyError:
        return False, (
            "Der E-Mail-Versand ist noch nicht vollständig konfiguriert. "
            "Bitte prüfe die Datei .streamlit/secrets.toml."
        )
    except ValueError:
        return False, "SMTP_PORT muss eine gültige Zahl sein."
    except (OSError, smtplib.SMTPException) as exc:
        return False, (
            "Die Nachricht konnte gerade nicht versendet werden. "
            "Bitte versuche es später erneut. "
            f"Technischer Hinweis: {type(exc).__name__}"
        )


def _portrait_header(
    *,
    portrait_data_url: str | None,
    subtitle: str,
) -> None:
    safe_portrait = html.escape(portrait_data_url or "", quote=True)
    avatar_html = (
        f'<img src="{safe_portrait}" alt="Portrait von Yana">'
        if safe_portrait
        else '<span aria-hidden="true">YP</span>'
    )

    st.html(
        f"""
        <div class="portfolio-chat">
            <div class="portfolio-chat-header">
                <div class="portfolio-chat-avatar">
                    {avatar_html}
                    <span class="portfolio-chat-status" aria-hidden="true"></span>
                </div>
                <div>
                    <strong>Yana Pfalzgraf</strong>
                    <span>{html.escape(subtitle)}</span>
                </div>
            </div>
        </div>
        """
    )


@st.dialog("Kontakt mit Yana", width="small")
def contact_form_dialog(portrait_data_url: str | None = None) -> None:
    """Zeigt ausschließlich das Kontaktformular."""
    init_chat_state()
    _portrait_header(
        portrait_data_url=portrait_data_url,
        subtitle="Direkte Nachricht senden",
    )

    st.markdown("### Direkt eine Nachricht senden")
    st.caption(
        "Pflichtfelder sind mit * markiert. Deine Angaben werden nur zur "
        "Bearbeitung der Kontaktanfrage verwendet."
    )

    with st.form("portfolio_contact_form", clear_on_submit=False):
        name = st.text_input("Name *", max_chars=100)
        sender_email = st.text_input("E-Mail-Adresse *", max_chars=180)
        company = st.text_input("Unternehmen", max_chars=140)
        message = st.text_area(
            "Nachricht *",
            height=150,
            max_chars=3000,
            placeholder=(
                "Zum Beispiel: Wir möchten gerne mit Ihnen über eine Position "
                "im Bereich Product Analytics sprechen."
            ),
        )
        privacy_accepted = st.checkbox(
            "Ich stimme der Verarbeitung meiner Angaben zur Bearbeitung "
            "dieser Kontaktanfrage zu. *"
        )

        submitted = st.form_submit_button(
            "Nachricht an Yana senden →",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        clean_name = name.strip()
        clean_email = sender_email.strip()
        clean_company = company.strip()
        clean_message = message.strip()

        if len(clean_name) < 2:
            st.error("Bitte gib deinen Namen ein.")
        elif not _EMAIL_PATTERN.match(clean_email):
            st.error("Bitte gib eine gültige E-Mail-Adresse ein.")
        elif len(clean_message) < 10:
            st.error("Bitte schreibe eine etwas ausführlichere Nachricht.")
        elif not privacy_accepted:
            st.error("Bitte bestätige die Verarbeitung deiner Angaben.")
        else:
            with st.spinner("Nachricht wird gesendet …"):
                success, feedback = send_contact_email(
                    name=clean_name,
                    sender_email=clean_email,
                    company=clean_company,
                    message=clean_message,
                )

            if success:
                st.success(feedback)
                st.balloons()
            else:
                st.error(feedback)

    st.divider()

    if st.button(
        "Fenster schließen",
        key="close_contact_form",
        use_container_width=True,
    ):
        st.session_state["contact_form_open"] = False
        st.rerun()

    st.html(
        '<p class="portfolio-chat-note">'
        "Das Formular sendet ausschließlich die ausdrücklich abgesendeten Angaben."
        "</p>"
    )


def render_floating_chat(portrait_data_url: str | None = None) -> None:
    """Rendert einen rechts unten fixierten Chat-Button mit Popover."""
    init_chat_state()

    with st.popover(
        "💬 Fragen zu Yanas Portfolio?",
        key="floating_portfolio_chat",
        help="Portfolio-Chat öffnen",
    ):
        _portrait_header(
            portrait_data_url=portrait_data_url,
            subtitle="Portfolio-Assistent · sofort verfügbar",
        )

        history = st.container(height=300)
        with history:
            for message in st.session_state["portfolio_chat_messages"]:
                with st.chat_message(message["role"]):
                    st.write(message["content"])

        prompt = st.chat_input(
            "Frage zum Portfolio eingeben …",
            key="floating_portfolio_chat_input",
        )

        if prompt:
            st.session_state["portfolio_chat_messages"].append(
                {"role": "user", "content": prompt}
            )
            st.session_state["portfolio_chat_messages"].append(
                {"role": "assistant", "content": create_chat_response(prompt)}
            )
            st.rerun()

        if st.button(
            "Chat neu starten",
            key="reset_floating_portfolio_chat",
            use_container_width=True,
        ):
            st.session_state["portfolio_chat_messages"] = [
                {"role": "assistant", "content": _INITIAL_MESSAGE}
            ]
            st.rerun()

        st.html(
            '<p class="portfolio-chat-note">'
            "Dieser Assistent beantwortet Fragen anhand der Inhalte dieser Portfolio-Seite."
            "</p>"
        )
