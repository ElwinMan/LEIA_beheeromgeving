<script lang="ts">
  import type { Bookmark } from "$lib/types/tool";
  import UpdateBookmarkModal from "$lib/components/modals/UpdateBookmarkModal.svelte";
  import { deleteBookmark } from "$lib/api";
  import { portal } from 'svelte-portal';
  import { tick } from 'svelte';
  import { createEventDispatcher } from 'svelte';

  let { bookmarks = [] } = $props();

  let modalComponent: any;

  let openIndex = $state<number | null>(null);
  let summaryRefs = $state<Array<HTMLElement | null>>([]);
  let dropdownLeft = $state(0);
  let dropdownTop = $state(0);

  const dispatch = createEventDispatcher<{ updated: void }>();

  function handleOpenModal(bookmark: Bookmark) {
    modalComponent.showModal(bookmark);
  }

  async function handleDelete(bookmarkId: number) {
    if (confirm('Weet je zeker dat je deze bookmark wilt verwijderen?')) {
      try {
        await deleteBookmark(String(bookmarkId));
        bookmarks = bookmarks.filter(b => b.id !== bookmarkId);
        dispatch('updated');
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
      dispatch('updated');
    }
  }

  function handleSummaryClick(idx: number) {
    if (openIndex === idx) {
      openIndex = null;
      window.removeEventListener('mousedown', handleClickOutside);
      return;
    }
    openIndex = idx;
    tick().then(() => {
      const ref = summaryRefs[idx];
      if (ref) {
        const rect = ref.getBoundingClientRect();
        dropdownLeft = rect.right - 160; // 160px for w-40
        dropdownTop = rect.bottom;
        window.addEventListener('mousedown', handleClickOutside);
      }
    });
  }

  function handleClickOutside(event: MouseEvent) {
    if (!event.target || !(event.target as HTMLElement).closest('.dropdown-content')) {
      openIndex = null;
      window.removeEventListener('mousedown', handleClickOutside);
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
          {#each bookmarks as bookmark, idx}
            <tr>
              <td class="text-sm font-bold">{bookmark.title}</td>
              <td class="text-sm">{bookmark.description}</td>
              <td class="text-sm relative">
                <div class="dropdown dropdown-end">
                  <button
                    bind:this={summaryRefs[idx]}
                    type="button"
                    class="btn btn-sm btn-ghost"
                    onclick={() => handleSummaryClick(idx)}
                  >
                    Opties
                    <img src="/icons/chevron-down.svg" alt="Chevron Down" class="ml-1 h-4 w-4" />
                  </button>
                  {#if openIndex === idx}
                    <ul
                      use:portal={'body'}
                      class="dropdown-content menu bg-base-100 rounded-box z-[1000] w-40 p-2 shadow"
                      style="position: absolute; left: {dropdownLeft}px; top: {dropdownTop}px;"
                    >
                      <li>
                        <button onclick={() => { handleOpenModal(bookmark); openIndex = null; }} class="flex items-center gap-2">
                          Bewerken
                        </button>
                      </li>
                      <li>
                        <button class="text-error" onclick={() => { handleDelete(bookmark.id); openIndex = null; }}>
                          Verwijderen
                        </button>
                      </li>
                    </ul>
                  {/if}
                </div>
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
      {#if bookmarks.length === 0}
        <div class="py-12 text-center opacity-70">Geen bookmarks gevonden.</div>
      {/if}
    </div>
  </div>
</div>