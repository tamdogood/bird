"""Anki integration tools using AnkiConnect for the Bird MCP server."""

from typing import Any, Optional
import httpx


class AnkiTools:
    """Tools for interacting with Anki via AnkiConnect."""

    def __init__(self, url: str = "http://localhost:8765"):
        """
        Initialize Anki tools with AnkiConnect URL.

        Args:
            url: AnkiConnect URL (default: http://localhost:8765)
        """
        self.url = url
        self.version = 6  # AnkiConnect API version

    async def _invoke(self, action: str, params: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        """
        Send a request to AnkiConnect.

        Args:
            action: AnkiConnect action name
            params: Parameters for the action

        Returns:
            Response from AnkiConnect
        """
        payload = {
            "action": action,
            "version": self.version,
        }
        if params:
            payload["params"] = params

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(self.url, json=payload)
                response.raise_for_status()
                result = response.json()

                if result.get("error"):
                    return {"success": False, "error": result["error"]}

                return {"success": True, "result": result.get("result")}

        except httpx.ConnectError:
            return {
                "success": False,
                "error": f"Could not connect to AnkiConnect at {self.url}. Make sure Anki is running with AnkiConnect installed.",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def create_deck(self, deck_name: str) -> dict[str, Any]:
        """
        Create a new deck in Anki.

        Args:
            deck_name: Name of the deck to create

        Returns:
            Success status and deck ID
        """
        result = await self._invoke("createDeck", {"deck": deck_name})
        if result["success"]:
            return {
                "success": True,
                "deck_id": result["result"],
                "message": f"Deck '{deck_name}' created successfully",
            }
        return result

    async def get_decks(self) -> dict[str, Any]:
        """
        Get all deck names and their IDs.

        Returns:
            List of all decks
        """
        result = await self._invoke("deckNamesAndIds")
        if result["success"]:
            decks = [{"name": name, "id": deck_id} for name, deck_id in result["result"].items()]
            return {"success": True, "decks": decks, "count": len(decks)}
        return result

    async def create_note(
        self,
        deck_name: str,
        front: str,
        back: str,
        note_type: str = "Basic",
        tags: Optional[list[str]] = None,
    ) -> dict[str, Any]:
        """
        Create a new note (card) in Anki.

        Args:
            deck_name: Name of the deck to add the note to
            front: Front of the card (question/prompt)
            back: Back of the card (answer)
            note_type: Type of note (default: "Basic")
            tags: List of tags to add to the note

        Returns:
            Success status and note ID
        """
        # Validate note type exists
        model_names_result = await self._invoke("modelNames")
        if not model_names_result["success"]:
            return model_names_result

        available_models = model_names_result["result"]
        if note_type not in available_models:
            return {
                "success": False,
                "error": f"Note type '{note_type}' not found. Available types: {', '.join(available_models)}",
            }

        note = {
            "deckName": deck_name,
            "modelName": note_type,
            "fields": {"Front": front, "Back": back},
            "tags": tags or [],
        }

        result = await self._invoke("addNote", {"note": note})
        if result["success"]:
            return {
                "success": True,
                "note_id": result["result"],
                "message": f"Note added to deck '{deck_name}'",
            }
        return result

    async def create_cloze_note(
        self,
        deck_name: str,
        text: str,
        tags: Optional[list[str]] = None,
        extra: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Create a cloze deletion note in Anki.

        Args:
            deck_name: Name of the deck to add the note to
            text: Text with cloze deletions (e.g., "{{c1::Paris}} is the capital of {{c2::France}}")
            tags: List of tags to add to the note
            extra: Additional information field

        Returns:
            Success status and note ID
        """
        fields = {"Text": text}
        if extra:
            fields["Extra"] = extra

        note = {
            "deckName": deck_name,
            "modelName": "Cloze",
            "fields": fields,
            "tags": tags or [],
        }

        result = await self._invoke("addNote", {"note": note})
        if result["success"]:
            return {
                "success": True,
                "note_id": result["result"],
                "message": f"Cloze note added to deck '{deck_name}'",
            }
        return result

    async def get_deck_stats(self, deck_name: str) -> dict[str, Any]:
        """
        Get statistics for a specific deck.

        Args:
            deck_name: Name of the deck

        Returns:
            Deck statistics including card counts and review info
        """
        # Get deck stats
        stats_result = await self._invoke("getDeckStats", {"decks": [deck_name]})
        if not stats_result["success"]:
            return stats_result

        deck_stats = stats_result["result"].get(deck_name, {})

        # Get card counts for the deck
        cards_result = await self._invoke(
            "findCards", {"query": f'deck:"{deck_name}"'}
        )
        total_cards = len(cards_result.get("result", [])) if cards_result["success"] else 0

        # Get new cards count
        new_cards_result = await self._invoke(
            "findCards", {"query": f'deck:"{deck_name}" is:new'}
        )
        new_cards = len(new_cards_result.get("result", [])) if new_cards_result["success"] else 0

        # Get cards due today
        due_cards_result = await self._invoke(
            "findCards", {"query": f'deck:"{deck_name}" is:due'}
        )
        due_cards = len(due_cards_result.get("result", [])) if due_cards_result["success"] else 0

        return {
            "success": True,
            "deck": deck_name,
            "stats": {
                "total_cards": total_cards,
                "new_cards": new_cards,
                "cards_due_today": due_cards,
                "new_cards_today": deck_stats.get("new_count", 0),
                "review_count": deck_stats.get("review_count", 0),
                "total_in_deck": deck_stats.get("total_in_deck", 0),
            },
        }

    async def get_all_stats(self) -> dict[str, Any]:
        """
        Get comprehensive statistics across all decks.

        Returns:
            Overall Anki statistics
        """
        # Get all decks
        decks_result = await self.get_decks()
        if not decks_result["success"]:
            return decks_result

        decks = decks_result["decks"]

        # Collect stats for each deck
        deck_stats_list = []
        total_cards = 0
        total_new = 0
        total_due = 0

        for deck in decks:
            deck_name = deck["name"]
            stats = await self.get_deck_stats(deck_name)

            if stats["success"]:
                deck_info = stats["stats"]
                deck_stats_list.append({"name": deck_name, **deck_info})
                total_cards += deck_info.get("total_cards", 0)
                total_new += deck_info.get("new_cards", 0)
                total_due += deck_info.get("cards_due_today", 0)

        return {
            "success": True,
            "overall_stats": {
                "total_decks": len(decks),
                "total_cards": total_cards,
                "total_new_cards": total_new,
                "total_cards_due_today": total_due,
            },
            "deck_stats": deck_stats_list,
        }

    async def update_deck_config(
        self,
        deck_name: str,
        new_cards_per_day: Optional[int] = None,
        reviews_per_day: Optional[int] = None,
    ) -> dict[str, Any]:
        """
        Update deck configuration settings.

        Args:
            deck_name: Name of the deck to update
            new_cards_per_day: Maximum new cards per day
            reviews_per_day: Maximum reviews per day

        Returns:
            Success status
        """
        # Get current deck config
        config_result = await self._invoke("getDeckConfig", {"deck": deck_name})
        if not config_result["success"]:
            return config_result

        config = config_result["result"]

        # Update config values
        if new_cards_per_day is not None:
            config["new"]["perDay"] = new_cards_per_day

        if reviews_per_day is not None:
            config["rev"]["perDay"] = reviews_per_day

        # Save updated config
        result = await self._invoke("saveDeckConfig", {"config": config})
        if result["success"]:
            return {
                "success": True,
                "message": f"Deck '{deck_name}' configuration updated",
                "new_cards_per_day": config["new"]["perDay"],
                "reviews_per_day": config["rev"]["perDay"],
            }
        return result

    async def add_tags_to_notes(
        self, note_ids: list[int], tags: list[str]
    ) -> dict[str, Any]:
        """
        Add tags to existing notes.

        Args:
            note_ids: List of note IDs
            tags: Tags to add

        Returns:
            Success status
        """
        tag_string = " ".join(tags)
        result = await self._invoke(
            "addTags", {"notes": note_ids, "tags": tag_string}
        )
        if result["success"]:
            return {
                "success": True,
                "message": f"Tags added to {len(note_ids)} notes",
            }
        return result

    async def find_notes(self, query: str) -> dict[str, Any]:
        """
        Find notes using Anki's search syntax.

        Args:
            query: Anki search query (e.g., "deck:French tag:verb", "is:due")

        Returns:
            List of matching note IDs
        """
        result = await self._invoke("findNotes", {"query": query})
        if result["success"]:
            note_ids = result["result"]
            return {
                "success": True,
                "note_ids": note_ids,
                "count": len(note_ids),
            }
        return result

    async def suspend_cards(self, card_ids: list[int]) -> dict[str, Any]:
        """
        Suspend cards (prevent them from appearing in reviews).

        Args:
            card_ids: List of card IDs to suspend

        Returns:
            Success status
        """
        result = await self._invoke("suspend", {"cards": card_ids})
        if result["success"]:
            return {
                "success": True,
                "message": f"Suspended {len(card_ids)} cards",
            }
        return result

    async def unsuspend_cards(self, card_ids: list[int]) -> dict[str, Any]:
        """
        Unsuspend cards (allow them to appear in reviews again).

        Args:
            card_ids: List of card IDs to unsuspend

        Returns:
            Success status
        """
        result = await self._invoke("unsuspend", {"cards": card_ids})
        if result["success"]:
            return {
                "success": True,
                "message": f"Unsuspended {len(card_ids)} cards",
            }
        return result

    async def get_note_types(self) -> dict[str, Any]:
        """
        Get all available note types (models).

        Returns:
            List of note type names
        """
        result = await self._invoke("modelNames")
        if result["success"]:
            return {
                "success": True,
                "note_types": result["result"],
                "count": len(result["result"]),
            }
        return result

    async def update_note(
        self,
        note_id: int,
        fields: dict[str, str],
        tags: Optional[list[str]] = None,
    ) -> dict[str, Any]:
        """
        Update an existing note's fields and tags.

        Args:
            note_id: ID of the note to update
            fields: Dictionary of field names to new values (e.g., {"Front": "...", "Back": "..."})
            tags: New tags to replace existing tags (optional)

        Returns:
            Success status
        """
        note_update = {"id": note_id, "fields": fields}
        if tags is not None:
            note_update["tags"] = tags

        result = await self._invoke("updateNoteFields", {"note": note_update})
        if result["success"]:
            return {"success": True, "message": f"Note {note_id} updated"}
        return result

    async def get_note_info(self, note_ids: list[int]) -> dict[str, Any]:
        """
        Get detailed information about specific notes.

        Args:
            note_ids: List of note IDs to retrieve

        Returns:
            Note information
        """
        result = await self._invoke("notesInfo", {"notes": note_ids})
        if result["success"]:
            return {
                "success": True,
                "notes": result["result"],
                "count": len(result["result"]),
            }
        return result

    async def delete_notes(self, note_ids: list[int]) -> dict[str, Any]:
        """
        Permanently delete notes.

        Args:
            note_ids: List of note IDs to delete

        Returns:
            Success status
        """
        result = await self._invoke("deleteNotes", {"notes": note_ids})
        if result["success"]:
            return {
                "success": True,
                "message": f"Deleted {len(note_ids)} notes",
            }
        return result
