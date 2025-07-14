<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { createDigitalTwin, bulkModifyToolAssociations, createViewer } from '$lib/api';
  import type { BulkToolOperation } from '$lib/types/digitalTwinAssociation';
  import type { DigitalTwin } from '$lib/types/digitalTwin';

  const dispatch = createEventDispatcher<{ created: DigitalTwin }>();

  let modalRef: HTMLDialogElement | null = null;

  // Form fields
  let name = '';
  let title = '';
  let subtitle = '';
  let owner = '';
  let isPrivate = false;
  let toolIds: number[] = [];

  export function showModal() {
    resetForm();
    modalRef?.showModal();
  }

  function resetForm() {
    name = '';
    title = '';
    subtitle = '';
    owner = '';
    isPrivate = false;
  }

  async function handleSubmit(event: Event) {
    event.preventDefault();

    try {
      const newTwin = await createDigitalTwin({
        name,
        title,
        subtitle,
        owner,
        private: isPrivate,
        last_updated:  new Date().toISOString()
      });

      // Create Viewer with default values
    await createViewer(newTwin.id);

    // Create default tools
    const defaultToolIds = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11];
    const operations: BulkToolOperation[] = defaultToolIds.map(id => ({
      tool_id: id,
      action: 'create'
    }));
    await bulkModifyToolAssociations(newTwin.id, operations);

    dispatch('created', newTwin);
    modalRef?.close();
  } catch (error) {
    console.error('Failed to create digital twin or viewer', error);
  }
}
</script>

<dialog bind:this={modalRef} class="modal">
  <form onsubmit={handleSubmit} class="modal-box space-y-4">
    <h3 class="text-lg font-bold">Digital Twin Aanmaken</h3>

    <input class="input input-bordered w-full" placeholder="Naam" bind:value={name} required />
    <input class="input input-bordered w-full" placeholder="Titel" bind:value={title} required />
    <input class="input input-bordered w-full" placeholder="Subtitel" bind:value={subtitle} />
    <input class="input input-bordered w-full" placeholder="Eigenaar" bind:value={owner} required />

    <label class="flex items-center gap-2">
      <input type="checkbox" class="checkbox" bind:checked={isPrivate} />
      Privé
    </label>

    <div class="flex justify-end gap-2 pt-4">
      <button type="button" class="btn btn-ghost" onclick={() => modalRef?.close()}>Annuleren</button>
      <button type="submit" class="btn btn-primary">Aanmaken</button>
    </div>
  </form>
</dialog>
