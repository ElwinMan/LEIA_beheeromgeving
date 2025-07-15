<script lang="ts">
  export let show = false;
  export let groupTitle = '';
  export let layerCount = 0;
  export let ondelete: (option: 'delete' | 'move') => void;
  export let oncancel: () => void;

  let selectedOption: 'delete' | 'move' = 'delete';

  function handleConfirm() {
    ondelete(selectedOption);
  }
</script>

{#if show}
  <div class="fixed inset-0 bg-black/40 z-50 flex items-center justify-center">
    <div class="bg-base-100 rounded-lg shadow-lg p-6 w-full max-w-md">
      <h2 class="text-lg font-bold mb-2 flex items-center gap-2">
        <img src="/icons/trash-2.svg" alt="Trash" class="w-5 h-5 text-error" />
        Groep verwijderen
      </h2>
      <p class="mb-4">
        Weet je zeker dat je de groep <b>{groupTitle}</b> wilt verwijderen?
        {#if layerCount > 0}
          <br />
          Deze groep bevat <b>{layerCount}</b> lagen. Wat wil je doen met deze lagen?
        {/if}
      </p>
      {#if layerCount > 0}
        <div class="mb-4 space-y-2">
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              type="radio"
              name="deleteOption"
              value="delete"
              bind:group={selectedOption}
              checked={selectedOption === 'delete'}
            />
            <span>Verwijder ook alle lagen in deze groep</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              type="radio"
              name="deleteOption"
              value="move"
              bind:group={selectedOption}
              checked={selectedOption === 'move'}
            />
            <span>Verplaats lagen naar ongegroepeerd</span>
          </label>
        </div>
      {/if}
      <div class="flex gap-2 justify-end">
        <button class="btn btn-error btn-sm" on:click={handleConfirm}>
          Verwijder
        </button>
        <button class="btn btn-ghost btn-sm" on:click={oncancel}>
          Annuleer
        </button>
      </div>
    </div>
  </div>
{/if}