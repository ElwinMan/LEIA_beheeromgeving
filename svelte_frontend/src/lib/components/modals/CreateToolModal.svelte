<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { createTool } from '$lib/api';
  import type { Tool } from '$lib/types/tool';
  import AlertBanner from '$lib/components/AlertBanner.svelte';

  let modalRef: HTMLDialogElement;
  const dispatch = createEventDispatcher<{ created: Tool }>();

  let name = '';
  let content = '';

  let errorBanner: InstanceType<typeof AlertBanner> | null = null;
  let successBanner: InstanceType<typeof AlertBanner> | null = null;

  const jsonPlaceholder = `{
  "variable": "value",
  "variable2": "value2",
  "number1": 1,
  "array": [
    {"variableInArray": "value3"}
  ]
}`;

  export function showModal() {
    name = '';
    content = '';
    errorBanner?.hide?.();
    successBanner?.hide?.();
    modalRef?.showModal();
  }

  async function handleSubmit(event: Event) {
    event.preventDefault();

    let payload: any = { name };
    if (content && content.trim() !== '') {
      try {
        payload.content = JSON.parse(content);
      } catch (e) {
        errorBanner?.show();
        return;
      }
    }

    try {
      const newTool = await createTool(payload);
      dispatch('created', newTool);
      successBanner?.show();
      modalRef.close();
      successBanner?.hide?.();
    } catch (error) {
      errorBanner?.show();
      console.error('Tool creation failed', error);
    }
  }
</script>

<AlertBanner
  bind:this={successBanner}
  type="success"
  message="Tool succesvol aangemaakt!"
/>

<dialog bind:this={modalRef} class="modal">
  <AlertBanner
    bind:this={errorBanner}
    type="error"
    message="Content moet geldig JSON zijn!"
  />

  <form
    on:submit|preventDefault={handleSubmit}
    class="modal-box grid w-full max-w-4xl grid-cols-4 items-center gap-4"
  >
    <h3 class="col-span-4 mb-4 text-lg font-bold">Nieuwe Tool Aanmaken</h3>

    <label for="name" class="pr-4 text-right font-semibold">Naam:</label>
    <input id="name" class="input input-bordered col-span-3 w-full" bind:value={name} required />

    <label for="content" class="pr-4 text-right font-semibold">Content:</label>
    <textarea
      id="content"
      class="textarea textarea-bordered col-span-3 w-full min-h-[12rem]"
      bind:value={content}
      rows="10"
      placeholder={jsonPlaceholder}
    ></textarea>

    <div class="col-span-4 mt-6 flex justify-end gap-2">
      <button type="button" class="btn btn-ghost" on:click={() => modalRef.close()}>Annuleren</button>
      <button type="submit" class="btn btn-primary">Aanmaken</button>
    </div>
  </form>
</dialog>