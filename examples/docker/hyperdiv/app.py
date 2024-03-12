import hyperdiv as hd


def main():
    with hd.box(padding=4, gap=1):
        hd.markdown("# Hyperdiv on Ploomber")

        hd.text("Hello!")

        state = hd.state(count=0)
        if hd.button("Increment").clicked:
            state.count += 1

        hd.text("You clicked", state.count, "times.")

        hd.markdown("Learn more at https://hyperdiv.io")


hd.run(main)
