import solara

# Declare reactive variables at the top level. Components using these variables
# will be re-executed when their values change.
sentence = solara.reactive("Solara makes our team more productive.")
word_limit = solara.reactive(10)


@solara.component
def Home():
    # Calculate word_count within the component to ensure re-execution when reactive variables change.
    word_count = len(sentence.value.split())

    solara.SliderInt("Word limit", value=word_limit, min=2, max=20)
    solara.InputText(label="Your sentence", value=sentence, continuous_update=True)

    # Display messages based on the current word count and word limit.
    if word_count >= int(word_limit.value):
        solara.Error(
            f"With {word_count} words, you passed the word limit of {word_limit.value}."
        )
    elif word_count >= int(0.8 * word_limit.value):
        solara.Warning(
            f"With {word_count} words, you are close to the word limit of {word_limit.value}."
        )
    else:
        solara.Success("Great short writing!")


routes = [solara.Route(path="__PROJECT_ID__", component=Home, label="Home")]
