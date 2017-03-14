#!/bin/bash
set -e
pdf="pdf"
html="html"
get_abs_filename() {
  # $1 : relative filename
  echo "$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
}
git fetch
git checkout origin/master notebooks/*
git checkout origin/master data/*

CURRENTPOS=$(pwd)
BASEDIR=$(cd $(dirname $BASH_SOURCE);pwd)
NBDIR=$BASEDIR/../notebooks
OUTPUTDIR=$1
NBEXT=.ipynb
HTML=.html
NBEXTNEW=.nbconvert.ipynb
NBEXTMD=.nbconvert.md
NBLIST=`echo 1-Motivation-and-Introduction 2-ROOT-Basics 3-ROOT-Macros 4-Graphs 5-Histograms 6-Functions-and-Parameter-Estimation 7-File-IO-and-Parallel-Analysis 8-ROOT-in-Python 9-Concluding-Remarks`
echo $CURRENTPOS
if [ "$2" = "html" ] || [ "$2" = "all" ]
then
	chapter=0
	for name in $NBLIST ;do
		jupyter nbconvert --ExecutePreprocessor.timeout=600 --to html $NBDIR/$name"$NBEXT"
		let chapter=chapter+1
	done
	python $BASEDIR/Build_html.py $NBLIST
  find $NBDIR -type f -name "*.html" -and -not -name "ROOT-Primer.html" | xargs rm
  cp $NBDIR/ROOT-Primer.html $OUTPUTDIR/ROOT-Primer.html
fi
if [ "$2" = "pdf" ] || [ "$2" = "all" ]
then
cat > mytemplate.tpl<< EOF
{% extends 'display_priority.tpl' %}
{% block in_prompt %}
{% endblock in_prompt %}

{% block output_prompt %}
{%- endblock output_prompt %}

{% block input %}
\`\`\`{% if nb.metadata.language_info %}{{ nb.metadata.language_info.name }}{% endif %}
{{ cell.source}}
\`\`\` 
{% endblock input %}

{% block error %}
{{ super() }}
{% endblock error %}

{% block traceback_line %}
{{ line | indent | strip_ansi }}
{% endblock traceback_line %}

{% block execute_result %}

{% block data_priority scoped %}
{{ super() }}
{% endblock %}
{% endblock execute_result %}

{% block stream %}
{{ output.text | indent }}
{% endblock stream %}

{% block data_svg %}
![svg]({{ output.metadata.filenames['image/svg+xml'] | path2url }})
{% endblock data_svg %}

{% block data_png %}
![{{cell.metadata.label}}]({{ output.metadata.filenames['image/png'] | path2url }})
{% endblock data_png %}

{% block data_jpg %}
![jpeg]({{ output.metadata.filenames['image/jpeg'] | path2url }})
{% endblock data_jpg %}

{% block data_latex %}
{{ output.data['text/latex'] }}
{% endblock data_latex %}

{% block data_html scoped %}
{{ output.data['text/html'] }}
{% endblock data_html %}

{% block data_markdown scoped %}
{{ output.data['text/markdown'] }}
{% endblock data_markdown %}

{% block data_text scoped %}
{{ output.data['text/plain'] | indent }}
{% endblock data_text %}

{% block markdowncell scoped %}
{% if 'remove' not in cell.metadata %}
{{ cell.source }}
{% endif %}
{% endblock markdowncell %}

{% block unknowncell scoped %}
unknown type  {{ cell.type }}
{% endblock unknowncell %}
EOF
	for name in $NBLIST ;do
	 	python $BASEDIR/removeJS.py $NBDIR/$name$NBEXT $NBDIR/"$name"_NOJS"$NBEXT";
		jupyter nbconvert --ExecutePreprocessor.timeout=2000 --to notebook --execute $NBDIR/"$name"_NOJS"$NBEXT";
		jupyter nbconvert  --to markdown $NBDIR/"$name"_NOJS"$NBEXTNEW" --template="mytemplate.tpl";
	done
	rm mytemplate.tpl
	cd $NBDIR
	pandoc --toc --template=$BASEDIR/mdtemplate.tex --highlight-style=tango $NBDIR/*_NOJS$NBEXTMD --latex-engine=pdflatex -o $NBDIR/ROOT-Primer_v0.pdf
	pdftk frontpage.pdf $NBDIR/ROOT-Primer_v0.pdf output $NBDIR/ROOT-Primer.pdf
	rm -rf *NOJS*
	rm $NBDIR/ROOT-Primer_v0.pdf
	cd $CURRENTPOS
	cp $NBDIR/ROOT-Primer.pdf $OUTPUTDIR/ROOT-Primer.pdf
fi
if [ "$2" != "html" ] && [ "$2" != "all" ] && [ "$2" != "pdf" ]
then
	echo "Wrong arguments. Accepted arguments are: 1rs argument location of output files - 2nd argument  pdf, html, all"
fi

rm -r notebooks
rm -r data 
git checkout dev