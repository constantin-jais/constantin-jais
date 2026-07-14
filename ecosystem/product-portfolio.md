# Libre IA — vision du portefeuille produit

Statut : doctrine produit cible, challengée le 2026-07-13.  
État d’exécution et maturité : [`status.md`](status.md).  
Métadonnées canoniques des dépôts : [`governance/repo-profiles.json`](governance/repo-profiles.json).

## 1. Périmètre public

Libre IA possède sept produits autonomes. Website est leur porte d’entrée publique ; Benchmarks est un programme de preuve. Ni Website ni Benchmarks ne doivent être comptés artificiellement comme un huitième ou un neuvième produit.

| Rôle | Éléments |
| --- | --- |
| Porte d’entrée | Website |
| Produits | Feed Radar, Notebook, AI Practices, Sessions, Boussole Politique, Spec Studio, Agent Board |
| Programme de preuve | Benchmarks |
| Infrastructure | Client Kit, Context Kit, Artifact Supply, Proof Kit, Agent Factory |

### Contrat d’URL public

`libre-ai.fr` est l’origine canonique. Website permet de comprendre ; un sous-domaine produit permet d’agir ; `preuves.libre-ai.fr` permet de vérifier. La décision complète et ses règles d’isolation vivent dans [ADR 0046](specs/shared/adrs/0046-public-domains-and-product-publication-gates.md).

| Nom public | Hôte réservé | État actuel |
| --- | --- | --- |
| Radar | `radar.libre-ai.fr` | `discovery` — DNS non activé |
| Carnet | `carnet.libre-ai.fr` | `discovery` — DNS non activé |
| Pratiques IA | `pratiques.libre-ai.fr` | `discovery` — DNS non activé |
| Sessions | `sessions.libre-ai.fr` | `discovery` — DNS non activé |
| Boussole Politique | `boussole.libre-ai.fr` | `discovery` — DNS non activé |
| Studio de spécification | `specs.libre-ai.fr` | `discovery` — DNS non activé |
| Missions | `missions.libre-ai.fr` | `discovery` — DNS non activé |
| Preuves | `preuves.libre-ai.fr` | `discovery` — DNS non activé |

Cette taxonomie décrit la cible. Elle ne prouve ni disponibilité, ni déploiement, ni qualité opérationnelle. Website peut publier un état honnête du portefeuille ; chaque CTA de lancement reste interdit tant que le produit concerné n’a pas atteint sa propre alpha publique vérifiée.

## 2. Doctrine commune

Chaque produit doit :

- résoudre seul un problème utilisateur durable ;
- fournir une première valeur sans compte global Libre IA ;
- rester utile sans adopter toute la stack ;
- minimiser les données et expliciter ce qui quitte l’appareil ou le workspace ;
- exporter un artefact lisible, versionné et réutilisable ;
- décrire erreurs, refus, fonctionnement dégradé et restauration ;
- séparer activité déclarée, résultat observé et preuve ;
- consommer l’infrastructure par contrat sans absorber sa responsabilité.

Une intégration entre produits est facultative. Aucun « super-produit » ne centralise les notes, apprentissages, positions politiques, missions ou historiques d’usage.

### Test anti-plateforme

Une capacité partagée n’est extraite que si :

1. un produit réel l’utilise dans un parcours prouvé ;
2. un second besoin indépendant confirme sa généralité ;
3. le contrat réduit la duplication sans déplacer le sens métier ;
4. l’extraction conserve un mode local ou remplaçable.

Avant ces quatre preuves, la capacité reste dans le produit qui en a besoin.

## 3. Contrat complet d’une vision produit

Ce document est la source humaine transverse ; `website/data/product-catalog.v3.json` en est la projection publique exécutable. Les dépôts produit possèdent leurs plans d’implémentation, mais ne recopient pas une deuxième vision divergente.

Toute vision produit doit rendre explicites :

1. le problème et le moment déclencheur ;
2. le public principal, sans persona marketing fictif ;
3. la première valeur observable ;
4. le parcours nominal et ses sorties ;
5. l’artefact portable produit ;
6. les données lues, créées, partagées et supprimées ;
7. le mode hors ligne ou dégradé ;
8. les refus et non-objectifs ;
9. la preuve minimale avant disponibilité ;
10. les dépendances facultatives avec les autres produits et l’infrastructure.

## 4. Les sept produits challengés

### Feed Radar — décider quoi lire

**Problème durable.** Une personne reçoit plus de signaux qu’elle ne peut en examiner et ne sait pas pourquoi un tri automatique a retenu ou écarté un élément.

**Première valeur.** Importer un petit OPML, appliquer une règle visible et obtenir une sélection dont chaque décision est explicable.

**Artefact.** `CuratedItemExport` : source originale, règle, décision, explication et provenance.

**Refus.** Feed Radar n’est ni un lecteur universel, ni un crawler générique, ni une mémoire de long terme, ni un arbitre de vérité.

**Challenge.** L’IA n’est utile que si elle améliore une décision inspectable. Un classement opaque, même performant, détruit la proposition de valeur.

**Première preuve de disponibilité.** Un parcours local import → règle → revue → export, rejouable sur fixtures et sur un flux réel borné, avec erreurs réseau et règles invalides visibles.

### Notebook — préparer un contexte sans ouvrir toute sa mémoire

**Problème durable.** Pour réutiliser ses notes dans un autre outil, une personne finit souvent par partager trop de contenu ou perd la trace de ce qui est sorti.

**Première valeur.** Capturer quelques blocs, sélectionner un sous-ensemble et prévisualiser exactement un paquet de contexte exportable.

**Artefact.** `NoteContextExport` : blocs choisis, liens nécessaires, provenance, exclusions et empreinte de version.

**Refus.** Notebook n’est pas un « second cerveau » omniscient, un moteur d’ingestion, un orchestrateur, ni une mémoire partagée implicite.

**Challenge.** L’éditeur de notes est nécessaire mais ne constitue pas le différenciateur. Le cœur produit est le passage privé → partagé, explicite et réversible.

**Première preuve de disponibilité.** Capture et lecture hors ligne, export prévisualisé, restauration depuis export et test négatif démontrant qu’un bloc non sélectionné ne sort pas.

### AI Practices — entraîner le jugement professionnel

**Problème durable.** Les formations IA récompensent souvent la récitation ou le score au lieu d’entraîner une décision responsable dans une situation réelle.

**Première valeur.** Résoudre une situation contextualisée, recevoir un feedback sourcé et repartir avec une action concrète à appliquer.

**Artefact.** Progression locale exportable : activités versionnées, réponses, feedbacks et axes à retravailler, sans classement nominatif.

**Refus.** AI Practices n’est ni une certification individuelle, ni un outil RH, ni un quiz de culture générale, ni un cursus exhaustif de machine learning.

**Challenge.** Les laboratoires techniques issus de l’ancien Website ne doivent pas décentrer le produit. Ils deviennent une piste facultative « construire et évaluer » destinée aux praticiens techniques ; le socle reste la décision professionnelle.

**Première preuve de disponibilité.** Un parcours privé complet avec activités approuvées humainement, feedback non punitif, export local et démonstration qu’aucun score nominatif n’est envoyé à une organisation.

### Sessions — apprendre et décider ensemble à partir de sources

**Problème durable.** Dans une session collective, sources, réponses privées, brouillons générés et synthèse validée se mélangent facilement.

**Première valeur.** Un facilitateur ouvre une session sourcée ; les participants contribuent selon un rôle ; la synthèse distingue provenance, brouillon et validation.

**Artefact.** Export de session par audience : sources, décisions et synthèse validée, sans réponses privées par défaut.

**Refus.** Sessions n’est ni un chatbot générique, ni un LMS asynchrone complet, ni le moteur des parcours individuels AI Practices.

**Challenge.** Le produit doit d’abord prouver une session synchrone utile avec peu de participants. La génération est optionnelle ; la facilitation et la séparation des données restent utiles sans modèle.

**Première preuve de disponibilité.** Une vraie session facilitée de bout en bout, avec citations contrôlées, reconnexion, rétention explicite et export par audience.

### Boussole Politique — comparer sans fabriquer une identité politique

**Problème durable.** Les comparateurs politiques réduisent souvent une personne à une étiquette et masquent sélection, dénominateur, abstentions ou incertitudes.

**Première valeur.** Se positionner localement sur des énoncés sourcés puis comparer uniquement avec les votes correspondants.

**Artefact.** Version de sélection : énoncés, méthode, sources, dénominateurs, abstentions et paramètres de calcul. Les réponses personnelles restent locales par défaut.

**Refus.** Boussole Politique n’est ni une consigne de vote, ni un classement moral, ni un sondage représentatif, ni un produit nécessitant de l’IA.

**Challenge.** Son appartenance à Libre IA se justifie par la méthode — local-first, explicabilité et preuve — pas par l’ajout artificiel d’un LLM. Sa gouvernance méthodologique doit rester autonome et bénéficier d’une revue indépendante.

**Première preuve de disponibilité.** Sélection canonique après fermeture des gates de symétrie et de couverture, revue juridique, calcul reproductible, accessibilité et absence démontrée de transmission des positions.

### Spec Studio — transformer l’ambiguïté en décisions vérifiables

**Problème durable.** Une conversation produit produit trop souvent des écrans ou tickets sans relier hypothèses, arbitrages et critères d’acceptation.

**Première valeur.** Formaliser un problème, rendre une décision manquante visible et produire un package qui échoue s’il n’est pas prêt.

**Artefact.** `SpecPackage` puis handoff planning-only : besoins, décisions, risques, preuves, validations et empreintes.

**Refus.** Spec Studio n’est ni un clone de Figma, ni un générateur de tickets, ni un agent d’implémentation, ni un moteur d’exécution.

**Challenge.** La quantité d’écrans ou de texte généré n’est pas un succès. Le produit gagne s’il réduit les décisions implicites et les reprises après handoff.

**Première preuve de disponibilité.** Un projet réel conversation → package validé → handoff refusé ou accepté pour des raisons compréhensibles, sans droit d’exécution.

### Agent Board — gouverner une mission agentique

**Problème durable.** Une équipe voit l’activité d’un agent mais pas toujours le mandat, le risque, le blocage, la décision humaine requise ou la preuve du résultat.

**Première valeur.** Proposer une mission, définir ses conditions d’acceptation et voir les gates à satisfaire avant toute exécution.

**Artefact.** `MissionRecord` : intention, périmètre, risque, approbations, événements, blocages, résultat et verdict humain.

**Refus.** Agent Board ne représente pas des profils d’agents, n’orchestre pas l’exécution, n’inspecte pas les outils et ne remplace pas un gestionnaire de projet généraliste.

**Challenge.** Une carte représente une mission, jamais un agent. L’activité déclarée par l’exécutant reste distincte du résultat vérifié. Agent Factory orchestre ; Agent Board donne aux humains la surface de décision.

**Première preuve de disponibilité.** Cycle fixture-backed proposer → approuver → exécuter via adapter simulé → bloquer/reprendre → accepter ou refuser, avec auteur et raison sur chaque transition.

## 5. Relations utiles, jamais obligatoires

```text
Radar selection ──► Carnet context ──► Studio de spécification ──► Missions ──► Preuves
                            │                        │                  │
                            └────► Sessions sources  └── planning ─────┘

Pratiques IA activity ──► Sessions facilitated mode ──► Preuves

Boussole Politique ──► Carnet source package (optionnel)
                    └─► Website methodology and correction reports
```

Règles :

- le handoff est visible et exportable ;
- le destinataire ne reçoit que les données choisies ;
- une indisponibilité d’infrastructure ne détruit pas l’artefact source ;
- aucune chaîne n’autorise automatiquement publication, exécution ou partage.

## 6. Échelle de preuve et état public

La maturité d’un dépôt et la disponibilité d’un produit sont deux axes différents.

| Niveau de preuve produit | Exigence minimale |
| --- | --- |
| Intention | problème, public, frontières et risques documentés |
| Contrat | modèle, fixtures, erreurs et invariants exécutables |
| Parcours local | scénario cœur réellement utilisable sur une machine propre |
| Alpha publique | URL ou artefact installable, accessibilité de base, export, limites et support documentés |
| Fiable | restauration, mises à jour, rollback, sécurité, opérations et incidents éprouvés |

Le terme public **« disponible »** exige au minimum une alpha publique réellement accessible. Une compilation, une fixture, un CLI partiel ou une page Website ne suffit pas.

| État public | Contrat |
| --- | --- |
| `discovery` | vision, contrat ou prototype ; aucune URL applicative |
| `private-alpha` | parcours borné non public ; aucune URL applicative |
| `public-alpha` | URL canonique et preuve datée du parcours cœur |
| `stable` | restauration, retrait, sécurité et opérations éprouvés |

## 7. Gate de publication par produit

Pour passer un produit à `public-alpha` :

- URL canonique exactement égale à son hôte réservé ;
- preuve publiée sous `preuves.libre-ai.fr/<slug>` ;
- parcours cœur exécuté dans un environnement propre ;
- état vide, erreur, refus et reprise vérifiés ;
- export lisible et restauration testée lorsque le produit crée des données ;
- données envoyées, conservées et supprimées documentées ;
- test clavier et viewport étroit pour les surfaces web ;
- dépendances, licence et provenance contrôlées ;
- responsable humain, date de preuve et limites publiés ;
- rollback ou retrait explicite disponible ;
- attestation de publication propre au produit.

Website conserve sa propre approbation humaine, mais n’attend plus les sept produits. Le catalogue supprime le CTA de lancement et affiche l’hôte comme réservé tant que la gate locale n’est pas satisfaite.

## 8. Réalité actuelle

Le cockpit détaillé canonique est [product-readiness.md](product-readiness.md). Cette section ne garde que la synthèse pour éviter la duplication entre la vision et l’audit quotidien.

| Fait transverse | Synthèse |
| --- | --- |
| Disponibilité | Les sept produits publics restent sous `public-alpha` ; aucun hôte public n’est activé. |
| Couche d’infrastructure | Agent Factory reste une infrastructure habilitante, traitée séparément du catalogue produit. |
| Doctrine de lecture | La maturité du dépôt, le nombre d’issues et la présence d’un parcours local ne suffisent pas à annoncer une disponibilité. |

Conclusion : la cible des sept produits reste cohérente, mais l’audit détaillé vit désormais dans le cockpit central. Website garde sa synthèse publique ; les statuts de dépôt ne sont jamais convertis automatiquement en disponibilité produit.

## 9. Ordre recommandé par dépendances de preuve

Cet ordre ne constitue pas une échéance commerciale.

1. **AI Practices et Feed Radar** : transformer leurs surfaces exécutables en parcours utilisateur complets.
2. **Spec Studio** : convertir le CLI contractuel en parcours local utilisable sans élargir l’exécution.
3. **Sessions** : prouver une session réelle, sourcée et exportable.
4. **Notebook et Agent Board** : implémenter le contrat de confidentialité Notebook et la projection locale consommant le moteur de mission Agent Board.
5. **Boussole Politique** : fermer les gates méthodologiques et juridiques avant le shell public.

Les briques partagées ne sont extraites qu’après apparition de deux besoins prouvés dans cet ordre de travail.
