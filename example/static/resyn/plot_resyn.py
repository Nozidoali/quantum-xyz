import pandas as pd
import matplotlib.pyplot as plt

FONT_SIZE = 18
LEFT = 0.15
RIGHT = 0.95
TOP = 0.95
BOTTOM = 0.15

customize_legend_names = {
    "initial": "Initial",
    "qiskit": "Qiskit Opt.",
    "bqskit_flow": "BQSKit Leap",
    "ours": "Ours",
    "n_g2_initial": "Initial",
    "n_g2_qiskit": "Qiskit Opt.",
    "n_g2_bqskit_flow": "BQSKit Leap",
    "n_g2_ours": "Ours",
    "fidelity_iinitial": "Initial",
    "fidelity_qiskit": "Qiskit Opt.",
    "fidelity_bqskit_flow": "BQSKit Leap",
    "fidelity_ours": "Ours",
}


def plot_fidelity():
    df = pd.read_csv("resynthesis.csv")

    # preprocessing: we set the bqskit_flow to initial if the optimized version is worse
    df["fidelity_bqskit_flow"] = df[["fidelity_initial", "fidelity_bqskit_flow"]].max(
        axis=1
    )

    # we first group the dataset using the name
    df = df.groupby("name")

    # for each group, we plot a bar plot
    for name, group in df:
        print(f"Plotting {name}")

        # we create a new df with the four methods
        datas = []
        for n_qubits in [3, 6, 9]:
            for method in ["initial", "qiskit", "bqskit_flow", "ours"]:
                data = {}
                data["n"] = n_qubits
                data["fidelity"] = group[group["n_qubits"] == n_qubits][
                    f"fidelity_{method}"
                ].values[0]
                data["method"] = method
                datas.append(data)

        df2 = pd.DataFrame(datas)

        # plot the bar plot, fix the order of the methods
        df2["method"] = pd.Categorical(
            df2["method"], ["initial", "qiskit", "bqskit_flow", "ours"]
        )

        # set color palette
        plt.figure()

        ax = df2.pivot(index="n", columns="method", values="fidelity").plot(
            kind="bar", stacked=False
        )

        # set the font of x and y labels
        plt.xlabel("Number of qubits", fontsize=FONT_SIZE, fontname="serif")
        plt.ylabel("Fidelity", fontsize=FONT_SIZE, fontname="serif")

        plt.xticks(fontsize=FONT_SIZE, fontname="serif", rotation=0)
        plt.yticks(fontsize=FONT_SIZE, fontname="serif", rotation=0)

        # get the handles and labels
        handles, labels = ax.get_legend_handles_labels()

        # replace the labels
        labels = [customize_legend_names[label] for label in labels]

        # plot the legend
        ax.legend(
            handles=handles,
            labels=labels,
            fontsize=FONT_SIZE,
            loc="upper left",
            prop={"family": "serif", "size": FONT_SIZE},
        )
        
        # set the margins
        plt.subplots_adjust(left=LEFT, right=RIGHT, top=TOP, bottom=BOTTOM)

        plt.savefig(f"resynthesis_fidelity_{name}.pdf")

def plot_cnot():
    df = pd.read_csv("resynthesis.csv")

    # preprocessing: we set the bqskit_flow to initial if the optimized version is worse
    df["n_g2_bqskit_flow"] = df[["n_g2_initial", "n_g2_bqskit_flow"]].min(axis=1)

    # we first group the dataset using the name
    df = df.groupby("name")

    # for each group, we plot a bar plot
    for name, group in df:
        print(f"Plotting {name}")

        # we create a new df with the four methods
        datas = []
        for n_qubits in [3, 6, 9]:
            for method in ["initial", "qiskit", "bqskit_flow", "ours"]:
                data = {}
                data["n"] = n_qubits
                data["n_cnot"] = group[group["n_qubits"] == n_qubits][
                    f"n_g2_{method}"
                ].values[0]
                data["method"] = method
                datas.append(data)

        df2 = pd.DataFrame(datas)

        # plot the bar plot, fix the order of the methods
        df2["method"] = pd.Categorical(
            df2["method"], ["initial", "qiskit", "bqskit_flow", "ours"]
        )

        # set color palette
        plt.figure()

        ax = df2.pivot(index="n", columns="method", values="n_cnot").plot(
            kind="bar", stacked=False
        )

        # set the font of x and y labels
        plt.xlabel("Number of qubits", fontsize=FONT_SIZE, fontname="serif")
        plt.ylabel("Number of CNOTs", fontsize=FONT_SIZE, fontname="serif")

        plt.xticks(fontsize=FONT_SIZE, fontname="serif", rotation=0)
        plt.yticks(fontsize=FONT_SIZE, fontname="serif", rotation=0)

        # get the handles and labels
        handles, labels = ax.get_legend_handles_labels()

        # replace the labels
        labels = [customize_legend_names[label] for label in labels]

        # plot the legend
        ax.legend(
            handles=handles,
            labels=labels,
            fontsize=FONT_SIZE,
            loc="upper left",
            prop={"family": "serif", "size": FONT_SIZE},
        )

        # set the margins
        plt.subplots_adjust(left=LEFT, right=RIGHT, top=TOP, bottom=BOTTOM)

        plt.savefig(f"resynthesis_{name}.pdf")


def plot_time():
    # plot the cpu time
    df = pd.read_csv("resynthesis_1.csv")

    # skip small benchmarks
    df = df[df["n_g2_initial"] > 10]

    # group by cnot count
    # df = df[df["initial_method"] == "m_flow"]

    df_n = df[df["initial_method"] == "n_flow"]
    df_n_1 = df_n[["n_g2_initial", "time_ours"]]
    df_n_1 = df_n_1.groupby("n_g2_initial").mean().reset_index()
    ax = df_n.plot.scatter(
        x="n_g2_initial", y="time_ours", marker="x", c="red", alpha=0.5
    )
    # line plot
    df_n_1.plot(x="n_g2_initial", y="time_ours", c="red", ax=ax)

    df_m = df[df["initial_method"] == "m_flow"]
    df_m_1 = df_m[["n_g2_initial", "time_ours"]]
    df_m_1 = df_m_1.groupby("n_g2_initial").mean().reset_index()
    df_m_1.plot.scatter(
        x="n_g2_initial", y="time_ours", marker="x", c="blue", ax=ax, alpha=0.5
    )
    # line plot
    df_m_1.plot(x="n_g2_initial", y="time_ours", c="blue", ax=ax)

    plt.xticks(fontsize=FONT_SIZE - 2, fontname="serif", rotation=0)
    plt.yticks(fontsize=FONT_SIZE - 2, fontname="serif", rotation=0)

    # log scale
    plt.xscale("log")
    plt.yscale("log")

    plt.xlabel("Number of CNOTs", fontsize=FONT_SIZE, fontname="serif")
    plt.ylabel("CPU time (s)", fontsize=FONT_SIZE, fontname="serif")

    # get the handles and labels
    handles, labels = ax.get_legend_handles_labels()

    # replace the labels
    labels = ["Dense states", "Sparse states"]

    # plot the legend
    ax.legend(
        handles=handles,
        labels=labels,
        fontsize=FONT_SIZE,
        loc="upper left",
        prop={"family": "serif", "size": FONT_SIZE},
    )

    plt.subplots_adjust(left=LEFT, right=RIGHT, top=TOP, bottom=BOTTOM)

    plt.savefig("resynthesis_time.pdf")

    plt.clf()


def plot_avg():
    # we process the average cnot of all the names
    df = pd.read_csv("resynthesis_1.csv")

    # preprocessing: we set the bqskit_flow to initial if the optimized version is worse
    df["n_g2_bqskit_flow"] = df[["n_g2_initial", "n_g2_bqskit_flow"]].min(axis=1)

    # we keep only the cnots
    df = df[
        ["n_qubits", "n_g2_initial", "n_g2_qiskit", "n_g2_bqskit_flow", "n_g2_ours"]
    ]

    # we add a row for the average, and the n_qubits column is called "average"
    df.loc["average"] = df.mean()
    df.loc["average", "n_qubits"] = "Avg."

    # change the dtype of n_qubits to string
    # df["n_qubits"] = df["n_qubits"].astype(str)
    print(df)

    # we keep only the n_qubits = 3, 6, 9
    df = df[df["n_qubits"].isin([3, 6, 9, "Avg."])]

    df = df.groupby("n_qubits").mean()

    # barplot
    ax = df.plot(kind="bar")

    # label the average using text
    cnot_impr = (df["n_g2_initial"] - df["n_g2_ours"]) / df["n_g2_initial"] * 100

    for i, v in enumerate(cnot_impr):
        height = df["n_g2_ours"].iloc[i]
        ax.text(
            i + 0.2,
            height + 5,
            f"{v:.2f}%",
            color="black",
            ha="center",
            fontsize=FONT_SIZE,
        )

    plt.xlabel("Number of qubits", fontsize=FONT_SIZE, fontname="serif")

    plt.ylabel("Average number of CNOTs", fontsize=FONT_SIZE, fontname="serif")

    plt.xticks(fontsize=FONT_SIZE, fontname="serif", rotation=0)
    plt.yticks(fontsize=FONT_SIZE, fontname="serif", rotation=0)

    plt.subplots_adjust(left=LEFT, right=RIGHT, top=TOP, bottom=BOTTOM)

    # get the handles and labels
    handles, labels = ax.get_legend_handles_labels()

    # replace the labels
    labels = [customize_legend_names[label] for label in labels]

    # plot the legend
    ax.legend(
        handles=handles,
        labels=labels,
        fontsize=FONT_SIZE,
        loc="upper left",
        prop={"family": "serif", "size": FONT_SIZE},
    )

    plt.savefig("resynthesis_avg.pdf")


if __name__ == "__main__":
    plot_cnot()
    plot_fidelity()