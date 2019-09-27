# NVDA-MarkdownForever
Une petite extension NVDA qui convertit facilement du contenu MarkDown ou HTML

* Auteurs : André-Abush Clause et contributeurs
* Licence : Licence publique générale GNU, version 2
* Télécharger [version stable][1]
* Télécharger [version en développement][2]
* Dépôt GitHub : [andre9642/NVDA-markdownForever][3]

## Commandes
- *NVDA+ALT+,* : mode interactif.
- *NVDA+ALT+b* : conversion Markdown vers HTML. Le résultat s'affiche dans votre navigateur par défaut.
- *NVDA+ALT+n* : conversion Markdown vers HTML. Le résultat s'affiche dans un tampon virtuel de NVDA.
- *NVDA+ALT+k* : conversion HTML vers Markdown. Le résultat s'affiche dans un tampon virtuel de NVDA.
- *NVDA+ALT+l* : conversion markdown en source HTML. Le résultat est affiché dans un tampon virtuel de NVDA.
- *NVDA+SHIFT+h* : copie le HTML généré dans le presse-papiers à partir d'un contenu Markdown. Une seule pressions copie en texte brut (source HTML), deux pressions rapides copient en HTML formaté.

### Notes

* Le *HTML formaté* peut être collé dans des applications comme Microsoft Word, Wordpad, Thunderbird, un champ de texte enrichi dans une page web, etc. Cependant, il ne peut pas être collé dans un éditeur de texte tel que Notepad, Notepad++, etc..
* Vous pouvez modifier ces raccourcis clavier dans les gestes de commandes de NVDA, dans la section — MarkDown Pour Toujours —.
* Il est recommandé de privilégier l'affichage dans le navigateur plutôt que le tampon virtuel de NVDA.
  Certaines balises telles que `<details>` ne sont pas supportées par le rendu du tampon virtuel.

## Dépendances incluses
- *markdown2* : <https://github.com/trentm/python-markdown2>
- *html2markdown* : <https://pypi.org/project/html2markdown/>
- *PyYAML*: <https://pypi.org/project/PyYAML/>

[1]: https://andreabc.net/projects/NVDA_addons/MarkdownForever/latest
[2]: https://andreabc.net/projects/NVDA_addons/MarkdownForever/latest?channel=dev
[3]: https://github.com/Andre9642/nvda-markdownForever
