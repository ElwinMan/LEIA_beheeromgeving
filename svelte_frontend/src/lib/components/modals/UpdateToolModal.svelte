<script lang="ts">
  import type { Tool } from '$lib/types/tool';
  import { createEventDispatcher } from 'svelte';
  import { updateTool } from '$lib/api';
  import AlertBanner from '$lib/components/AlertBanner.svelte';
  import MissingRequiredFields from '$lib/components/MissingRequiredFields.svelte';
  import HelpTooltip from '$lib/components/HelpTooltip.svelte';

  export let tool: Tool | null = null;
  let modalRef: HTMLDialogElement;

  let name: string = '';
  let content: string | null = null;
  let missingFields: string[] = [];
  let errorBanner: InstanceType<typeof AlertBanner> | null = null;
  let errorMessage: string = "Content moet geldig JSON zijn!";

  const jsonPlaceholder = `{
  "variable": "value",
  "variable2": "value2",
  "number1": 1,
  "array": [
    {"variableInArray": "value3"}
  ]
}`;

  const dispatch = createEventDispatcher();

  function resetModal() {
    missingFields = [];
    errorBanner?.hide?.();
  }

  export function showModal(t: Tool) {
    tool = t;
    name = t.name || '';
    content = t.content ? JSON.stringify(t.content, null, 2) : null;
    errorMessage = "Content moet geldig JSON zijn!";
    resetModal();
    modalRef.showModal();
  }

  function getMissingRequiredFields(): string[] {
    const fields: { label: string; value: any }[] = [
      { label: 'Naam', value: name }
    ];
    return fields.filter(f => !f.value || (typeof f.value === 'string' && !f.value.trim())).map(f => f.label);
  }

  async function handleSubmit(event: Event) {
    event.preventDefault();
    errorMessage = "Content moet geldig JSON zijn!";
    missingFields = getMissingRequiredFields();
    if (missingFields.length > 0) return;

    if (!tool) return;
    let payload: any = {
      name,
      last_updated: new Date().toISOString()
    };
    if (typeof content === 'string' && content.trim() !== '') {
      try {
        payload.content = JSON.parse(content);
        errorBanner?.hide?.();
      } catch (e) {
        errorBanner?.show();
        return;
      }
    } else {
      errorBanner?.hide?.();
    }

    try {
      const updated = await updateTool(String(tool.id), payload);
      dispatch('updated', updated);
      modalRef.close();
    } catch (error: any) {
      if (
        error?.status === 409 ||
        (error?.message && (
          error.message.includes('duplicate key')
        ))
      ) {
        errorMessage = "Deze naam is al in gebruik. Kies een andere naam.";
      } else {
        errorMessage = "Content moet geldig JSON zijn!";
      }
      errorBanner?.show();
      console.error('Update failed', error);
    }
  }
</script>


<dialog bind:this={modalRef} class="modal">
  <AlertBanner
    bind:this={errorBanner}
    type="error"
    message={errorMessage}
  />
  <form on:submit|preventDefault={handleSubmit} class="modal-box w-full max-w-4xl space-y-4">
    <h3 class="mb-4 text-lg font-bold">Tool bewerken</h3>

    <div class="form-control">
      <MissingRequiredFields {missingFields} />
    </div>

    <div class="form-control">
      <label for="name" class="label font-semibold">
        Naam <span class="text-error">*</span>
        <HelpTooltip tip="De naam van de tool. Deze moet uniek zijn." position="right" />
      </label>
      <input id="name" class="input input-bordered w-full" bind:value={name} />
    </div>

    <div class="form-control">
      <label for="content" class="label font-semibold">
        Content:
        <HelpTooltip tip="De configuratie van de tool in JSON formaat. Dit veld is optioneel." position="right" />
      </label>
      <textarea
        id="content"
        class="textarea textarea-bordered w-full min-h-[12rem]"
        bind:value={content}
        rows="10"
        placeholder={jsonPlaceholder}
      ></textarea>
    </div>

    <div class="flex justify-end gap-2 pt-4">
      <button type="button" class="btn btn-ghost" on:click={() => { modalRef.close(); resetModal(); }}>Annuleren</button>
      <button type="submit" class="btn btn-primary">Opslaan</button>
    </div>
  </form>
</dialog>