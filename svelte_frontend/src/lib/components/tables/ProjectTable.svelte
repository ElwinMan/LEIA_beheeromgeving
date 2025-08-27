<script lang="ts">
  import type { Project } from "$lib/types/tool";
  import UpdateProjectModal from "$lib/components/modals/UpdateProjectModal.svelte";
  import { deleteProject, fetchProjectsPaginated } from "$lib/api";
  import { portal } from 'svelte-portal';
  import { tick } from 'svelte';
  import { createEventDispatcher } from 'svelte';
  import TableControls from './TableControls.svelte';
  import SortableTableHeader from "$lib/components/tables/SortableTableHeader.svelte";
  import DateTimeCell from "$lib/components/DateTimeCell.svelte";

  let modalComponent: any;

  let openIndex = $state<number | null>(null);
  let summaryRefs = $state<Array<HTMLElement | null>>([]);
  let dropdownLeft = $state(0);
  let dropdownTop = $state(0);

  // State for search and debounce
  let search = $state('');
  let debouncedSearch = $state('');
  let searchTimeout: ReturnType<typeof setTimeout> | null = null;

  // Pagination state
  let page = $state(1);
  let pageSize = $state(10);
  let total = $state(0);

  // Sorting state
  let sortColumn = $state('name');
  let sortDirection = $state<'asc' | 'desc'>('asc');

  let projects: Project[] = $state([]);

  const dispatch = createEventDispatcher<{ updated: void }>();

  function handleOpenModal(project: Project) {
    modalComponent.showModal(project);
  }

  async function handleDelete(projectId: number) {
    if (confirm('Weet je zeker dat je dit project wilt verwijderen?')) {
      try {
        await deleteProject(String(projectId));
        await loadProjects();
        dispatch('updated');
      } catch (err) {
        alert('Verwijderen mislukt. Controleer de server.');
        console.error(err);
      }
    }
  }

  function handleUpdated(event: CustomEvent<Project>) {
    loadProjects();
    dispatch('updated');
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
        dropdownLeft = rect.right - 160;
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

  // Debounce search input
  function onSearchChange(newValue: string) {
    if (searchTimeout) clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
      debouncedSearch = newValue;
      page = 1;
    }, 1000);
  }

  async function loadProjects() {
    try {
      const data = await fetchProjectsPaginated(
        debouncedSearch,
        page,
        pageSize,
        sortColumn,
        sortDirection
      );
      projects = data.results;
      total = data.total;
    } catch (err) {
      projects = [];
      total = 0;
    }
  }

  $effect(() => {
    loadProjects();
  });

  function setSort(column: string) {
    if (sortColumn === column) {
      sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
    } else {
      sortColumn = column;
      sortDirection = 'asc';
    }
    page = 1;
  }

  function gotoPage(p: number) {
    if (p < 1 || p > totalPages()) return;
    page = p;
  }

  function totalPages() {
    return Math.max(1, Math.ceil(total / pageSize));
  }
</script>

<UpdateProjectModal bind:this={modalComponent} on:updated={handleUpdated} />

<TableControls
  {search}
  onSearch={onSearchChange}
  {page}
  totalPages={totalPages()}
  {pageSize}
  onPageChange={gotoPage}
  onPageSizeChange={(size) => { pageSize = size; page = 1; }}
/>

<div class="card bg-base-100 shadow-xl">
  <div class="card-body p-0">
    <div class="overflow-x-auto">
      <table class="table-xs table-pin-rows table">
        <thead>
          <tr>
            <SortableTableHeader
              column="name"
              label="Naam"
              {sortColumn}
              {sortDirection}
              {setSort}
            />
            <SortableTableHeader
              column="description"
              label="Beschrijving"
              {sortColumn}
              {sortDirection}
              {setSort}
            />
            <SortableTableHeader
              column="last_updated"
              label="Gewijzigd"
              {sortColumn}
              {sortDirection}
              {setSort}
            />
            <th class="bg-base-200 font-bold">Acties</th>
          </tr>
        </thead>
        <tbody>
          {#each projects as project, idx}
            <tr>
              <td class="text-sm font-bold">{project.name}</td>
              <td class="text-sm">{project.description}</td>
              <td class="text-sm"><DateTimeCell value={project.last_updated} /></td>
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
                        <button onclick={() => { handleOpenModal(project); openIndex = null; }} class="flex items-center gap-2">
                          <img src="/icons/settings.svg" alt="Settings" class="h-4 w-4" />
                          Bewerken
                        </button>
                      </li>
                      <li>
                        <button class="text-error" onclick={() => { handleDelete(project.id); openIndex = null; }}>
                          <img src="/icons/trash-2.svg" alt="Settings" class="h-4 w-4" />
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
      {#if projects.length === 0}
        <div class="py-12 text-center opacity-70">Geen projecten gevonden.</div>
      {/if}
    </div>
  </div>
</div>