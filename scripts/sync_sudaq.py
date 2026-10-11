#!/usr/bin/env python3
"""Build the Sudaq Reveal.js lecture from the Obsidian outline and local audio dataset.
The source vault is read-only. Only the generated Hugo bundle is written.
"""
from pathlib import Path
import argparse, html, re, shutil, subprocess

DEFAULT = Path.home() / 'Documents/PKM/obsidian/PROJECTS/author-lectures/taraqtaş_2026/лекция Sudaq şive dili - tarixımızdan bir menbadır.md'
TITLE = 'Sudaq şive dili - tarixımızdan bir menbadır'

def md(text):
    return subprocess.run(['pandoc','-f','markdown-implicit_figures','-t','html5','--wrap=none'], input=text,text=True,capture_output=True,check=True).stdout.strip()

def build(source, repo):
    blocks = [b.strip() for b in re.split(r'(?m)^___\s*$',source.read_text()) if b.strip()]
    assets = repo/'static/talks/sudaq-2026/assets'
    assets.mkdir(parents=True,exist_ok=True)
    dataset_path = repo/'content/data/data1/index.md'
    dataset = dataset_path.read_text()
    records={}
    for line in dataset.splitlines():
        match=re.search(r'<audio controls src="audio/([^"]+)"',line)
        if match:
            cells=[x.strip() for x in line.strip('|').split('|')]
            records[match[1]]=(cells[0],cells[3],cells[1])
    for file in source.parent.joinpath('files').glob('*.png'):
        if file.name in ('taraqtas-1.png','taraqtas-2.png','dil_xaritası.png','dataset-1.png','dataset-2.png'):
            shutil.copy2(file,assets/file.name)
    used=set()
    def audio(names):
        rows=['<table class="audio-table"><thead><tr><th scope="col">Yazıda</th><th scope="col">Transkriptsiya</th><th scope="col">Ses yazısı</th></tr></thead><tbody>']
        for file in names:
            ipa,orth,origin=records[file]
            used.add(file)
            rows.append('<tr><td>'+html.escape(orth)+'</td><td class="ipa">['+html.escape(ipa)+']</td><td><audio controls preload="metadata" aria-label="'+html.escape(orth,quote=True)+'" src="./assets/audio/'+file+'"></audio></td></tr>')
        rows.append('</tbody></table>')
        return '\n'.join(rows)
    slides=[]
    def add(title,body,layout='text',note='',kicker=''):
        slides.append((title,body,layout,note,kicker))
    def table_parts(block,count):
        title,rest=block.split('\n',1)
        rows=[line for line in rest.splitlines() if line.startswith('|')]
        return title,rest, [ '\n'.join(rows[:2]+rows[i:i+count]) for i in range(2,len(rows),count)]
    add(TITLE,'<p class="author">Asan Emirsale</p>','cover', 'Основа: авторская заметка из Obsidian. Судакские формы и транскрипции сохранены.','Qırım 2040')
    for block in blocks:
        title,_,body=block.partition('\n')
        if title=='Sudaq tarafında birinci köyler':
            ps=[p for p in body.strip().split('\n\n') if p.strip()]
            add(title,md(ps[0])+md('> '+ps[1])+md('> '+ps[2]),'quote-pair','Устные предания из авторской основы, запись 2009 года.','2009 sene yazan rivayet')
        elif title=='Nasın bir külle?':
            add(title,md('Eki biñ yıl ögüne Taraqtaş külleler hem köyler endi vardı.')+'<div class="paired-figures"><figure><img src="./assets/taraqtas-1.png" alt="Археологические объекты в районе Таракташа: карта и фотография горы"></figure><figure><img src="./assets/taraqtas-2.png" alt="Комплекс памятников позднеантичного времени: план культового комплекса, поселение Таракташ V и находки"></figure></div>','archaeology-pair','Иллюстрации из авторской основы, рис. 12 и 14. Полная библиографическая ссылка в заметке не указана.')
        elif title=='Tatqara küllesi':
            body=body.replace('Arap tarixçı','Tarixçı')
            add(title,md(body)+'<p class="caption">Tatqara / Taraqtaş: yerini añlatqan bir faraziye</p>','text','В исходнике Рашид ад-Дин назван арабским историком; это определение убрано. Его труд «Джами ат-таварих» создан при дворе ильханов в Иране: https://www.iranicaonline.org/articles/jame-al-tawarik/ . Ссылка подтверждает автора и труд, но не конкретный фрагмент о Таткаре. Его точное издание и страницу нужно уточнить. Локализация Таткары на горе Таракташ остаётся авторской гипотезой.')
        elif title.startswith('Klanlar sisteması'):
            add(title,md(body),'clans','Иерархия и примеры воспроизводят авторскую систему. Соотношение tuqum / tayfa / küçük tayfa описывает конкретную местную традицию.')
        elif title=='Sudaq qalqı içine tayfa adları':
            body=body.replace('yapar^1','yapar').replace('^1 (','(')
            body=body.replace('Çoq sayısından sebep - böle adlar - başqa dilden qalan miras.', 'Bu adlar başqa dilden qalan miras olmaq munkün.')
            add(title,md(body),'names','Источник, указанный автором: Чалаш Сейтосман, «Suvdağ ses», 1999, № 12. Неясная тюркская этимология сама по себе не доказывает происхождение из другого языка; тезис передан как гипотеза.')
        elif title=='Hem Sudaqta hem Kafkazda tapılan adlar':
            _,_,parts=table_parts(block,7)
            for i,p in enumerate(parts):
                add(title,md(p),'name-table','Сопоставления из авторской заметки. Это сходства форм, а не установленные этимологии. Для каждого имени нужны словарный источник, исторические формы и фонетические соответствия.',f'Tayfa adları · {i+1}/{len(parts)}')
        elif title=='Avropda eski diller xaritası':
            add(title,'<figure><img src="./assets/dil_xaritası.png" alt="Авторская обзорная карта древних языков Европы, Малой Азии и Кавказа"><figcaption>Faraziyeler de gösterilgen, bir devriñ keskin xaritası dögül</figcaption></figure>','map','Авторская обзорная карта из хранилища. На ней совмещены разновременные языки и гипотезы об их классификации. «Сино-кавказская» макросемья и ряд привязок остаются гипотетическими; вопросительные знаки важны. Карту нельзя читать как единовременное достоверное распределение языковых семей.')
        elif title.startswith('Türkiy dillerden hem'):
            add('Sudaqçanıñ tutuq sesleri', '<p>Dedigimiz dilde de mot seslerimiz çoq.</p>'+audio(['kI_taraqtas_kIata_diyik.mp3','ghu_taraqtas_01.mp3','kI_taraqtas_kaci_dogul_k1ati.mp3']),'audio','Примеры и транскрипции: авторский датасет /data/data1/. Колонка с источником записи скрыта во всех аудиопримерах. Источники остаются в исходном датасете. Абсолютное утверждение об отсутствии этих звуков во всех тюркских языках не повторяется.')
        elif title=='Sudaqçada tutuq sesler misal cedveli':
            add(title,'<div class="paired-figures"><figure><img src="./assets/dataset-1.png" alt="Полный первый снимок страницы авторского фонетического датасета"></figure><figure><img src="./assets/dataset-2.png" alt="Полный второй снимок страницы авторского фонетического датасета"></figure></div><p class="dataset-link"><a href="../../data/data1/" target="_blank" rel="noopener">asan-emirsaleh.github.io/data/data1/</a></p>','dataset-pair','Авторский набор аудиофрагментов и транскрипций: /data/data1/. Оба снимка страницы показаны целиком по указанию автора.')
        elif title=='Güç qoşuyıp sozunan tutuq sesleri':
            add(title,audio(['z_taraqtas_uzzun.mp3','bb_taraqtas_o_bbasqa.mp3','ss_ssalma_war.mp3']),'audio','Авторский датасет, раздел Fortis and consonant doubling. Сохранены транскрипции uzʼːun, o bːaʃqa, sːaɫma war без нормализации.')
        elif title.startswith('Patlayan tutuq sesler'):
            add("Patlayan tutuq sesler - [p'], [k'], [q']",audio(['pI_taraqtas_p1elen.mp3','kI_taraqtas_kIata_diyik.mp3','qIh_taraqtas_mamutov.mp3','kI_taraqtas_k1ati.mp3','pI_taraqtas_atce-kata.mp3']),'audio-five','Авторский датасет, Ejective consonants и Palatalized ejective consonants.')
        elif title.startswith('Dudaqlatıyıp diyen tutuq sesler - ğ'):
            add('Dudaqlatıyıp diyen tutuq sesler: ğʷ, kʷ, qʷ',audio(['ghu_taraqtas_01.mp3','w_taraqtas_kot_kwot.mp3','w_taraqtas_qwoz.mp3']),'audio','Авторский датасет, Labialization. В заголовок добавлено qʷ, поскольку выбранный автором qʷoz иллюстрирует qʷ. Дополнительный пример kʷʰot kʷʰot иллюстрирует указанное в основе kʷ.')
        elif title.startswith('Dudaqlatıyıp diyen tutuq sesler - ş'):
            add('Dudaqlatıyıp diyen tutuq sesler: şʷ, sʷ, cʷ',audio(['w-sw_taraqtas_swudaq_2.mp3','w-cw_taraqtas_cwoydim.mp3','s_taraqtas_gunes_a_bu.mp3','sw_taraqtas_gunes_qonay.mp3']),'audio','Авторский датасет, Labialization. В паре güneş abu / güneş qonay сохранено различие [ɕ] / [ɕʷ], как в датасете. Написание coydum воспроизводит датасет; в плане было coydım.')
        elif title.startswith('Retrofleks tutuq sesler'):
            add(title,audio(['ssh_taraqtas_mamutov.mp3','ssh_taraqtas_02.mp3']),'audio','Заголовок перечисляет категории из плана. Выбранные два аудиопримера непосредственно показывают [ʂ]; они не демонстрируют каждую из трёх категорий. Транскрипции сохранены из датасета.')
        elif title=='Nasın bir dillerde böle sesler var':
            _,_,parts=table_parts(block,8)
            for i,p in enumerate(parts):
                p=p.replace('Türkiy diller |','Türkiy diller* |')
                add(title,md(p)+'<p class="caption">* «−»: bu işçi cedvelde belgilenmegen</p>','feature-table','Авторская рабочая сравнительная таблица сохранена целиком, включая все 16 строк. «+» и «−» воспроизводят авторскую схему. «−» не доказывает отсутствия звука во всех языках семьи. Для типологического вывода нужно сравнивать конкретные языки и различать фонемы, аллофоны, геминацию и контекстную лабиализацию.',f'Seslerniñ müqayesesi · {i+1}/{len(parts)}')
        elif title=='Sozuq sesler':
            rows='\n'.join(l for l in body.splitlines() if l.startswith('|')).replace('Arif','Arif')
            add(title,'<div class="vowel-comparison"><div>'+md(rows)+'<p class="legend"><span class="sudaq-color">qırmızlı: Sudaqça</span><br><span class="standard-color">Kök: edebiy qırımtatarca</span></p></div><figure><img src="./assets/vowels.svg" alt="Схема гласных: судакские [ɑː], [ɐ], [ə] выделены красным, литературные [a], [ɯ] выделены синим"></figure></div>','vowels','Выделены только звуки, перечисленные в авторской таблице. Положение символов схематическое, не акустическое измерение и не полный инвентарь гласных. Артикуляторные оси и размещение IPA опираются на https://www.internationalphoneticassociation.org/content/ipa-vowels . Схема создана как редактируемый SVG для этого слайда.')
        elif title.startswith('Edebiyat dili fonetikası'):
            add('Edebiyat dili hem Sudaq fonetikası',md('| Yazıda | Transkriptsiya | Kirillnen |\n| --- | --- | --- |\n| qazmaya | [qɑzmɐjɑ] | къазмыя |\n| yapmaya | [yɑpmɐjɑ] | япмея |'),'forms','Три формы в каждой строке взяты из авторской заметки. Это разные способы передачи формы, а не автоматически подтверждённая цепочка исторических звуковых изменений. Не нужно озвучивать стрелки как установленную хронологию.')
        elif title=='Sudaqçada sözler deñiştirmesi':
            _,_,parts=table_parts(block,5)
            for i,p in enumerate(parts):
                p=p.replace('Судакский вариант','Sudaqça').replace('Ожидаемый тюркский вариант','Beklengen türkiy şekil')
                add(title,md(p),'word-table','Авторские сопоставления из основы. Заголовок второй колонки означает предполагаемую сравнительную форму, а не универсальную форму всех тюркских языков.',f'Sözler · {i+1}/{len(parts)}')
        elif title.startswith('"o" sözüni'):
            add('«o» sözüni tekrar-tekrar işletmesi',md(body),'pronouns','Все семь авторских сопоставлений сохранены, включая орфографические особенности. Это иллюстрации употребления из основы; грамматический статус повторов и их сходство с другими языками требуют отдельного анализа.')
        else:
            raise ValueError('Неизвестный раздел в основе: '+title)
    sections=[]
    for num,(title,body,layout,note,kicker) in enumerate(slides,1):
        label=f'<div class="eyebrow">{html.escape(kicker)}</div>' if kicker else ''
        back='<a class="back-link" href="../">← Все доклады</a>' if layout=='cover' else ''
        sections.append(f'<section class="slide layout-{layout}" id="slide-{num}" data-slide="{num}"><div class="frame">{label}<h1>{html.escape(title)}</h1><div class="body">{body}</div>{back}</div><aside class="notes">{md(note)}</aside></section>')
    bundle=repo/'content/talks/sudaq-2026'
    bundle.mkdir(parents=True,exist_ok=True)
    front='---\ntitle: "'+TITLE+'"\ndate: 2026-10-11\ndraft: false\nlayout: reveal-sudaq\ndescription: "Sudaq şive dili, Taraqtaş, tayfa adları hem fonetik misaller."\nsummary: "Авторская лекция о судакском говоре, родовых именах и крымско-кавказских параллелях с аудиопримерами."\ntags: ["linguistics", "Sudaq", "Qırım 2040"]\nauthor: ["Asan Emirsale"]\n---\n\n'
    (bundle/'index.md').write_text(front+'<!-- Сгенерировано scripts/sync_sudaq.py из основы Obsidian. -->\n\n'+'\n\n'.join(sections)+'\n')
    audio_dir=assets/'audio'; audio_dir.mkdir(exist_ok=True)
    for file in sorted(used):
        shutil.copy2(dataset_path.parent/'audio'/file,audio_dir/file)
    (bundle/'audio-sources.tsv').write_text('file\ttranscription\torthographic form\tsource\n'+'\n'.join('\t'.join((f,*records[f])) for f in sorted(used))+'\n')
    print(f'{len(slides)} слайдов, {len(used)} аудиофайлов: {bundle / "index.md"}')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,default=DEFAULT)
    parser.add_argument('--repo',type=Path,default=Path(__file__).resolve().parents[1])
    args=parser.parse_args()
    build(args.source,args.repo)
