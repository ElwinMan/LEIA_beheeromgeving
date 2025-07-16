<script lang="ts">
  import type { Cesium } from "$lib/types/tool";

  export let cesiums: Cesium[] = [];
</script>

<div class="card bg-base-100 shadow-xl">
  <div class="card-body p-0">
    <div class="overflow-x-auto">
      <table class="table-xs table-pin-rows table">
        <thead>
          <tr>
            <th class="bg-base-200 font-bold">URL</th>
            <th class="bg-base-200 font-bold">Vertex Normals</th>
            <th class="bg-base-200 font-bold">Acties</th>
          </tr>
        </thead>
        <tbody>
          {#each cesiums as cesium}
            <tr>
              <td>{cesium.url}</td>
              <td>{cesium.vertexNormals}</td>
              <td>
                <a href={`/tools/cesium/${cesium.id}`} class="btn btn-xs btn-ghost">Opties</a>
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
      {#if cesiums.length === 0}
        <div class="py-12 text-center opacity-70">Geen Cesium cesiums gevonden.</div>
      {/if}
    </div>
  </div>
</div>