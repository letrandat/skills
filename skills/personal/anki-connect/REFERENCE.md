# AnkiConnect Reference

This is the disclosed reference for [`anki-connect`](SKILL.md).

## Search Syntax Reference (for `findNotes`/`findCards`)

- Separate terms by spaces; terms are ANDed by default.
- Use `or`, parentheses, and `-` for NOT logic.
- Use `deck:Name`, `tag:tagname`, `note:ModelName`, `card:CardName`.
- Use `front:...` or other field names to limit by field.
- Use `re:` for regex, `w:` for word-boundary searches, `nc:` to ignore accents.
- Use `is:due`, `is:new`, `is:learn`, `is:review`, `is:suspended`, `is:buried` to filter card states.
- Use `prop:` searches for properties like interval or due date.
- Escape special characters with quotes or backslashes as needed.

## Action Catalog

### Card Actions
- `getEaseFactors`
- `setEaseFactors`
- `setSpecificValueOfCard`
- `suspend`
- `unsuspend`
- `suspended`
- `areSuspended`
- `areDue`
- `getIntervals`
- `findCards`
- `cardsToNotes`
- `cardsModTime`
- `cardsInfo`
- `forgetCards`
- `relearnCards`
- `answerCards`
- `setDueDate`
- `changeDeck`

### Deck Actions
- `deckNames`
- `deckNamesAndIds`
- `getDecks`
- `createDeck`
- `changeDeck`
- `deleteDecks`
- `getDeckConfig`
- `saveDeckConfig`
- `setDeckConfigId`
- `cloneDeckConfigId`
- `removeDeckConfigId`
- `getDeckStats`

### Graphical Actions
- `guiBrowse`
- `guiSelectCard`
- `guiSelectedNotes`
- `guiAddCards`
- `guiEditNote`
- `guiAddNoteSetData`
- `guiCurrentCard`
- `guiStartCardTimer`
- `guiShowQuestion`
- `guiShowAnswer`
- `guiAnswerCard`
- `guiUndo`
- `guiDeckOverview`
- `guiDeckBrowser`
- `guiDeckReview`
- `guiImportFile`
- `guiExitAnki`
- `guiCheckDatabase`
- `guiPlayAudio`

### Media Actions
- `storeMediaFile`
- `retrieveMediaFile`
- `getMediaFilesNames`
- `getMediaDirPath`
- `deleteMediaFile`

### Miscellaneous Actions
- `requestPermission`
- `version`
- `apiReflect`
- `sync`
- `getProfiles`
- `getActiveProfile`
- `loadProfile`
- `multi`
- `exportPackage`
- `importPackage`
- `reloadCollection`

### Model Actions
- `modelNames`
- `modelNamesAndIds`
- `findModelsById`
- `findModelsByName`
- `modelFieldNames`
- `modelFieldDescriptions`
- `modelFieldFonts`
- `modelFieldsOnTemplates`
- `createModel`
- `modelTemplates`
- `modelStyling`
- `updateModelTemplates`
- `updateModelStyling`
- `findAndReplaceInModels`
- `modelTemplateRename`
- `modelTemplateReposition`
- `modelTemplateAdd`
- `modelTemplateRemove`
- `modelFieldRename`
- `modelFieldReposition`
- `modelFieldAdd`
- `modelFieldRemove`
- `modelFieldSetFont`
- `modelFieldSetFontSize`
- `modelFieldSetDescription`

### Note Actions
- `addNote`
- `addNotes`
- `canAddNotes`
- `canAddNotesWithErrorDetail`
- `updateNoteFields`
- `updateNote`
- `updateNoteModel`
- `updateNoteTags`
- `getNoteTags`
- `addTags`
- `removeTags`
- `getTags`
- `clearUnusedTags`
- `replaceTags`
- `replaceTagsInAllNotes`
- `findNotes`
- `notesInfo`
- `notesModTime`
- `deleteNotes`
- `removeEmptyNotes`

### Statistic Actions
- `getNumCardsReviewedToday`
- `getNumCardsReviewedByDay`
- `getCollectionStatsHTML`
- `cardReviews`
- `getReviewsOfCards`
- `getLatestReviewID`
- `insertReviews`
