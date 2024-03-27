import streamlit as st
import dotenv
import os
from src.app import App
import traceback


def main():
    st.set_page_config(
        page_title="PROMPT-BUILDER",
        layout="wide",
    )
    app = App()
    dotenv.load_dotenv(".env")

    st.title("🛠️ PROMPT-BUILDER")

    placeholder = st.empty()
    # Read the README.md file
    with open('README.md', 'r') as file:
        readme = file.read()

    # Add a divider
    placeholder.markdown("---")
    placeholder.markdown(readme)

    # A title is included in the README.md file
    st.sidebar.title("🎨 INPUTS")

    key = os.getenv("OPENAI_API_KEY", None)
    if key is None:
        st.sidebar.write(
            "You can find or create your OpenAI API key at https://platform.openai.com/account/api-keys. This app "
            "doesn't store your API key. It is only used to make requests to the OpenAI API.")
        key = st.sidebar.text_input("OpenAI API Key", type="password")
        st.sidebar.markdown("---")
    prompt = st.sidebar.text_area("Prompt to optimize", placeholder="Write the prompt you want to optimize here",
                                  height=500)
    button_clicked = st.sidebar.button("Optimize")
    if button_clicked:
        placeholder.empty()
        try:
            app.key = key
        except Exception as e:
            if os.getenv("logging", "INFO") == "DEBUG":
                st.error(str(e) + ": " + traceback.format_exc())
            else:
                st.error(str(e))
            return
        response = app.run(prompt=prompt)

        if response["status"] == "error":
            st.error(response["message"])
            return

        st.markdown("---")
        st.header("📊 OUTPUTS")
        st.header("🚀 Optimized Prompt")
        st.code(response["optimized_prompt"], language="txt", line_numbers=False)
        st.warning("⚠️ Please review the optimized prompt before using it in production. "
                   "Remember that the model may still make mistakes. You can adjust the prompt manually if needed.")
        st.header("❗️ Required Info")
        formatting = ("<div style='background-color: lightgrey;  color: black; box-shadow: 0px 2px 4px rgba(0, 0, 0, "
                      "0.1); padding: 10px; border-radius: 5px; margin: 5px;'>{input}</div>")
        st.write(formatting.format(input=response["required_info"]), unsafe_allow_html=True)

        st.markdown("---")
        st.write(
            "Happy with your results? Consider [buying me a coffee ☕️](https://www.buymeacoffee.com/boonmaarten) ("
            "totally optional, I made this for myself first), and feel free to reach out to me on [LinkedIn]("
            "https://www.linkedin.com/in/maarten-boon2003/) if you have any questions or feedback.")


if __name__ == '__main__':
    main()
