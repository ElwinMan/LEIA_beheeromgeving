<script>
	export let data;
    const { tool } = data;
</script>

<h1>{tool.title}</h1>
<p>Type: {tool.type}</p>
<p>Url: {tool.url}</p>
<p>FeatureName: {tool.featureName}</p>
<p>isbackground: {tool.isBackground ? 'true' : 'false'}</p>