<script>
	export let data;
	const { digitalTwin } = data;
</script>

<h1>{digitalTwin.name}</h1>
<p>ID: {digitalTwin.id}</p>
<p>Title: {digitalTwin.title}</p>
<p>Subtitle: {digitalTwin.subtitle}</p>

<h2>Layer Associations</h2>
<ul>
  {#each digitalTwin.layer_associations as layer, i}
    <li>
      #{i + 1} – Layer ID: {layer.layer_id},
      Default: {layer.is_default ? 'Yes' : 'No'},
      Sort Order: {layer.sort_order},
      Group ID: {layer.group_id ?? 'None'}
    </li>
  {/each}
</ul>

<h2>Tool Associations</h2>
<ul>
  {#each digitalTwin.tool_associations as tool}
    <li>Tool ID: {tool.tool_id}</li>
  {/each}
</ul>
