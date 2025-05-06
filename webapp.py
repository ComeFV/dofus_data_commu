import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import numpy as np

st.title("Dofus Forum data analysis")
st.write(
    "This is a web application to analyze Dofus forum data. The data were retrieved on th 5th of may 2025 and manually treated to apply tags. subposts (responses to posts) were excluded from the analysis"
)

df = pd.read_csv("data/dofus_posts_no_sub_clean_labeled.csv")
# convert the tag columns to a col of lists
df["tags"] = df["tags"].apply(lambda x: eval(x) if isinstance(x, str) else x)

st.subheader("Methodology for labeling")
st.markdown(
    """
    The topics are labeled manually based on the content of the post.
     * Once a label is defined, a detection with keywords is created to automatically apply the label to other posts
     * Then all remaining posts are manually checked to catch false positive or false negatives, and edit the keywords detection if necessary.
     * **The keyword 'Autre' regroups all topics with very few instances.**
     * There are still mistakes present notably for 'Rework songes' which is not always for rework.
     * Complete list of keywords can be found at the end.
    """
)

st.subheader("Data overview")
with st.expander("Show raw data"):
    st.write(df)


#########################
st.header("📊 Data analysis")

# Display key numbers
col1, col2 = st.columns(2)

with col1:
    total_posts = len(df)
    st.metric(label="Total Posts", value=f"{total_posts:,}")

with col2:
    unique_users = df["pseudo"].nunique()
    st.metric(label="Unique Users", value=f"{unique_users:,}")

df_count = df.groupby("day").count()
df_count = df_count.reset_index()
df_count["day"] = df_count["day"].astype(str)
fig = px.bar(df_count, x="day", y="comment",
                     title="Nombre de posts par jour",
                     labels={"day": "Date", "count": "Nombre de posts"},
                     color_discrete_sequence=["#636EFA"])
fig.update_layout(
    xaxis_title="Date",
    yaxis_title="Nombre de posts",
    xaxis_tickangle=-45,
    xaxis_tickmode="array",
    xaxis_tickvals=df_count["day"].tolist(),
    xaxis_ticktext=df_count["day"].tolist(),
)
fig.update_traces(marker_line_color='black', marker_line_width=1.5, opacity=0.6)
st.plotly_chart(fig, use_container_width=True)
#########################

df_tags = df.explode("tags")
# print(df_tags["tags"].value_counts().reset_index(name='count'))
fig2= px.bar(df_tags["tags"].value_counts().reset_index(name='count'),
                     x="tags", y="count",
                     title="Nombre de posts par label",
                     labels={"tags": "Tag", "count": "Nombre de posts"},
                     color_discrete_sequence=["#636EFA"])
fig2.update_layout(
    xaxis_title="label",
    yaxis_title="Nombre de posts",
    xaxis_tickangle=-45,
    xaxis_tickmode="array",
    xaxis_tickvals=df_tags["tags"].value_counts().index.tolist(),
    xaxis_ticktext=df_tags["tags"].value_counts().index.tolist(),
    height=600,
)
fig2.update_traces(marker_line_color='black', marker_line_width=1.5, opacity=0.6)
st.plotly_chart(fig2, use_container_width=True)

#########################

df_tags_filtered = df_tags[df_tags["tags"] != "Autre"]
df_tags_filtered = df_tags_filtered["tags"].value_counts(normalize=True).reset_index(name='proportion')
fig3 = go.Figure()
fig3.add_trace(
    go.Pie(
        labels=df_tags_filtered["tags"],
        values=df_tags_filtered["proportion"],
        textinfo='label+percent',
        textposition="inside",
        showlegend=False))
fig3.update_layout(
    title_text="Proportion des labels SANS 'Autre'",
    title_x=0.5,
    height=600
)

st.plotly_chart(fig3, use_container_width=True)
# rename tag into label
df_tags_filtered = df_tags_filtered.rename(columns={"tags": "label", "count": "proportion"})
df_tags_filtered["proportion"] = df_tags_filtered["proportion"].apply(lambda x: round(x * 100, 1))
df_tags_filtered["nombre de posts"] = df_tags[df_tags["tags"] != "Autre"]["tags"].value_counts().reset_index(name='count')["count"]
st.write(df_tags_filtered)
#########################

df_users = df.groupby("pseudo").count()
df_users = df_users.reset_index()
df_users = df_users.sort_values(by="comment", ascending=False)
df_users = df_users[df_users["comment"] > 2]
fig4 = px.bar(df_users, x="pseudo", y="comment",
                        title="Nombre de posts par utilisateur (minimum 2)",
                        labels={"pseudo": "Utilisateur", "comment": "Nombre de posts"},
                        color_discrete_sequence=["#636EFA"])
fig4.update_layout(
    xaxis_title="Utilisateur",
    yaxis_title="Nombre de posts",
    xaxis_tickangle=-45,
    xaxis_tickmode="array",
    xaxis_tickvals=df_users["pseudo"].tolist(),
    xaxis_ticktext=df_users["pseudo"].tolist(),
)
st.plotly_chart(fig4, use_container_width=True)

#########################

st.subheader("Data exploration by label")
tag_list = df["tags"].explode().unique().tolist()
selected_tag = st.selectbox(
    "Select a label to explore",
    options=tag_list,
    index=tag_list.index("Autre"),
)
df_selected = df[df["tags"].apply(lambda x: selected_tag in x)]
st.write(f"Number of posts with label '{selected_tag}': {len(df_selected)}")
st.write("**Double click on a cell to view in full**")
st.dataframe(df_selected[["comment", "tags", "pseudo", "day"]].sort_values(by="day", ascending=False).reset_index(drop=True))

#########################

st.subheader("Data exploration by user")
user_list = df["pseudo"].unique().tolist()
selected_user = st.selectbox(
    "Select a user to explore",
    options=user_list,
    index=2)
df_user = df[df["pseudo"] == selected_user]

st.write(f"Number of posts by user '{selected_user}': {len(df_user)}")
st.dataframe(df_user[["comment", "tags", "pseudo", "day"]].sort_values(by="day", ascending=False).reset_index(drop=True))


# Define tag logic
TAG_LOGIC = {
    "Eklames dans craft potion": "any of ['eklame', 'éklame', 'ekhlame', 'eclame', 'potion']",
    "Équilibrage des classes": "(any of ['équilibrage', 'equilibrage'] and 'classe') or (any of ['nerf', 'revalorise', ' up ', 'refonte'] and any of ['ecaflip', 'sacrieur', 'sadi', 'forgelance', 'roublard', 'enutrof', 'enu', 'sram', 'cra', 'pandawa', 'xelor', 'sacri', 'élio', 'éniripsa', 'ougi', 'osa', 'zobal'])",
    "compensations": "any of ['dedomaton', 'rollback', 'compensation']",
    "Mode héros": "any of ['mode héro', 'dofus hero', 'mode hero'] and not 'héroïque'",
    "Séparation pvp & pvm": "any of ['pvp', 'pvm'] and any of ['sépar', 'différen', 'dissoci', 'distinct', 'équilibrage sur']",
    "quête Dofus Ocre / craft PDA": "any of ['archis', 'ocre', 'pda', 'moisson'] and not 'médiocre'",
    "Bots": "any of ['bots', 'botting', 'professionels du kama', 'triche', 'les bot']",
    "drops rares en combat": "('combat' and 'rare') or ('drop' and any of ['rare', 'très bas'])",
    "drops des dofus": "any of ['drop', 'loot'] and 'dofus'",
    "Debug / performance": "any of ['bug', 'buuug', 'fuite', ' lag', 'tester', 'crash', 'freeze'] or ('auto' and any of ['follow', 'pilote'])",
    "anciennes maps de combat": "'cartes de combat' or ('map' and ' de combat')",
    "Mafias pépites/pl": "'mafia' and any of ['pépites', ' pl']",
    "rework songes": "'songes'",
    "Génération de pépites": "any of ['génér', 'annulez'] and any of ['pépite', 'pepite']",
    "combats de quêtes": "'combat' and 'quête'",
    "Rework AVA": "any of ['mode ava', 'en ava', 'de l\'ava', 'd\'ava'] and not any of ['mode avan', 'en avan', 'de l\'avan', 'd\'avan']",
    "mode créature": "any of ['mode créature', 'mode creature']",
    "changelogs plus exhaustifs / complets": "any of ['changelog', 'patchnote', 'liste de change', 'donner des explications']",
    "bestiaire par défaut sur la zone": "'encyclopédie' and 'zone'",
    "Besoin de sites externes (DofusNoob)": "('dofus' and 'noob') or 'sites annexes'",
    "retour upvotes/downvotes sur Forum Dofus)": "'forum' and 'vote'",
    "Plus de Communication directement en jeu": "(any of ['communica', 'info'] and 'en jeu') or 'arrêter x'",
    "Améliorations des Interface": "any of ['interface', 'hdv']",
    "Améliorer Kolizéum (recompenses, matchmaking, etc.)": "any of ['améliorer', 'refonte'] and 'koli'",
    "Métiers liés au compte": "'métiers' and 'compte'",
    "Meilleure Modération": "any of ['modérat', 'modos']",
    "Rework élevage": "any of ['muldo', 'élevage', 'enclos']",
    "Remettre les Traques": "'traque'",
    "Rework vieux contenus (quêtes, donjons, etc.)": "'donjons demandant des recherches' or ('refonte' and 'quêtes')",
    "Fusion Kolizeum (pionner/historique)": "'fusion kolizeum' and 'pionnier'",
    "rework Forgemagie": "any of ['fm', 'forgemagie']",
    "Rework guildes/Alliances": "any of ['guilde', 'alliance'] and any of ['amélioration', 'revalorisation', 'supprimer', 'redonner', 'intérêt', 'revoir']",
    "fonctionnalité communautaires (Recherche de groupe/mercenariat)": "'groupe' and any of ['recherche', 'communautaire']",
    "Rework Percepteurs": "'percepteur'",
    "Direction artistique": "'la da '",
    "action sur le PL (encadrement, interdiction, etc)": "any of ['le pl ', 'du pl ', 'glementation du pl', 'le pl.', 'les pratique pl']",
    "retour Mode tactique": "'mode' and 'tactique'",
    "implémenter Attitudes/emotes etc": "any of ['attitude', 'emote', 'émote']",
    "ajout de tutoriels sur les mécaniques de jeu": "'tutoriel'",
    "rework des maisons (housing)": "'housing'",
    "manque d'Identité de classe": "'identité' and 'classe'",
    "modulation de niveau (wakfu)": "'modulation'",
    "Autre": "(no match)"
}

with st.expander("Show keywords/logic expressions"):

    selected_tags = st.multiselect("Select labels(s) to display", options=list(TAG_LOGIC.keys()), default=[])
    show_all = st.checkbox("Show all", value=False)

    # Display logic
    st.subheader("📋 labeling Rules")

    if show_all:
        for tag, rule in TAG_LOGIC.items():
            st.markdown(f"**🔖 {tag}**  \n→ {rule}")
    elif selected_tags:
        for tag in selected_tags:
            st.markdown(f"**🔖 {tag}**  \n→ {TAG_LOGIC[tag]}")
    else:
        st.info("Select labels(s) or check 'Show all'.")
