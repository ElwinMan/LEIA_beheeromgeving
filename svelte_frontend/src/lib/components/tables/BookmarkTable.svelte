<script lang="ts">
  import type { Bookmark } from "$lib/types/tool";
  import UpdateBookmarkModal from "$lib/components/modals/UpdateBookmarkModal.svelte";
  import { deleteBookmark } from "$lib/api";

  export let bookmarks: Bookmark[] = [];

  let modalComponent: any;

  function handleOpenModal(bookmark: Bookmark) {
    modalComponent.showModal(bookmark);
  }

  async function handleDelete(bookmarkId: number) {
    if (confirm('Weet je zeker dat je deze bookmark wilt verwijderen?')) {
      try {
        await deleteBookmark(String(bookmarkId));
        bookmarks = bookmarks.filter(b => b.id !== bookmarkId);
      } catch (err) {
        alert('Verwijderen mislukt. Controleer de server.');
        console.error(err);
      }
    }
  }

  function handleUpdated(event: CustomEvent<Bookmark>) {
    const updatedBookmark = event.detail;
    const idx = bookmarks.findIndex(b => b.id === updatedBookmark.id);
    if (idx > -1) {
      bookmarks[idx] = updatedBookmark;
      bookmarks = [...bookmarks];
    }
  }
</script>

<UpdateBookmarkModal bind:this={modalComponent} on:updated={handleUpdated} />

<div class="card bg-base-100 shadow-xl">
  <div class="card-body p-0">
    <div class="overflow-x-auto">
      <table class="table-xs table-pin-rows table">
        <thead>
          <tr>
            <th class="bg-base-200 font-bold">Titel</th>
            <th class="bg-base-200 font-bold">Beschrijving</th>
            <th class="bg-base-200 font-bold">Acties</th>
          </tr>
        </thead>
        <tbody>
          {#each bookmarks as bookmark}
            <tr>
              <td class="text-sm font-bold">{bookmark.title}</td>
              <td class="text-sm">{bookmark.description}</td>
              <td class="text-sm relative">
                <details class="dropdown dropdown-end">
                  <summary class="btn btn-sm btn-ghost">
                    Opties
                    <img src="/icons/chevron-down.svg" alt="Chevron Down" class="ml-1 h-4 w-4" />
                  </summary>
                  <ul class="menu dropdown-content bg-base-100 rounded-box z-[1] w-40 p-2 shadow">
                    <li>
                      <button on:click={() => handleOpenModal(bookmark)} class="flex items-center gap-2">
                        Bewerken
                      </button>
                    </li>
                    <li>
                      <button class="text-error" on:click={() => handleDelete(bookmark.id)}>
                        Verwijderen
                      </button>
                    </li>
                  </ul>
                </details>
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
      <div class="h-32"></div>
      {#if bookmarks.length === 0}
        <div class="py-12 text-center opacity-70">Geen bookmarks gevonden.</div>
      {/if}
    </div>
  </div>
</div>