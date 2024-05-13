from h2o_wave import main, app, Q, ui, handle_on, data
from dataclasses import dataclass
from typing import Optional, List
import pandas as pd
import openpyxl

async def init(q: Q) -> None:
    await setup_app(q)

async def initialize_app(q: Q):
    q.app.initialized = True
    q.user.client_data = ClientData()
    q.user.client_data.read_dados()

@app('/')
async def serve(q: Q):
    if not q.app.initialized:
        q.app.initialized = True

    if not q.user.initialized:
        q.user.user_inputs = UserInputs()
        q.user.user_inputs.reset()
        q.user.client_data = ClientData()
        q.user.client_data.read_dados(q)
        q.user.initialized = True

    if not q.client.initialized:
        await initialize_layout(q)
        q.client.cards = set()
        q.client.initialized = True
        await init(q)

    q.user.user_inputs.update(q.args)
    q.user.client_data.set_data_info(q)
    await handle_on(q)
    await setup_app(q)
    await q.page.save()

async def initialize_layout(q: Q):
        q.page['meta'] = ui.meta_card(box='',
                                      theme='h2o-dark')

        q.page['header'] = ui.header_card(box='1 1 11 1',
                title='Analise Risco de Evasão por Aluno - Secretaria da Educação do Estado',
                subtitle='Prova de Conceito para previsão de probabilidade de evasão escolar a partir do histórico de frequência e notas dos alunos de Londrina e Guarapuava',
                image='https://wave.h2o.ai/img/h2o-logo.svg',
                # color='transparent'
        )

        q.page['footer'] = ui.footer_card(box='1 10 3 1', caption='Made with 💛 by Tarea.')

@dataclass
class UserInputs:
    aluno: Optional[str] = ''

    def reset(self):
        # df_init = pd.read_excel('POC_Alunos_testOOT_predictions.xlsx')
        df_init = pd.read_excel('final.xlsx')
        df_init['CGM'] = df_init['CGM'].astype("string")

        init_aluno = list(df_init['CGM'].unique())[0]
        self.aluno = init_aluno
        del df_init
        return

    def update(self, q_args):
        if q_args.reset:
            self.reset()
            return

        if q_args.aluno_combobox:
            self.aluno = q_args.aluno_combobox

@dataclass
class ClientData:
    veiculo: Optional[List] = None

    def read_dados(self, q):
        # df = pd.read_excel('POC_Alunos_testOOT_predictions.xlsx')
        df = pd.read_excel('final.xlsx')
        df['CGM'] = df['CGM'].astype("string")
        self.dados = df
        self.set_data_info(q)

    def set_data_info(self, q):
        self.aluno = list(self.dados['CGM'].unique())


def get_data_row(q):
    data = q.user.client_data.dados
    data = data[['CGM', 'Prob_Evasao']]
    data['Prob_Evasao'] = round(data['Prob_Evasao']*100, 2)

    columns=[
            ui.table_column(name='CGM', label='Aluno'),
            ui.table_column(name='Prob_Evasao', label='Prob Evasão (%)', sortable=True),
            ]

    rows = [
            ui.table_row(name=str(row[0]), cells=[str(cell) for cell in row]) for i, row in data.iterrows()
            ]

    return rows, columns

async def setup_app(q: Q) -> None:
    # seedpr_img = 'https://www.comunicacao.pr.gov.br/sites/default/arquivos_restritos/files/imagem/2021-07/60f9e56ce05a9-GovernoParanaH%28rgb-Positivo%29.jpg'
    #
    # q.page['image'] = ui.form_card(box='10 1 3 1',
    #         items=[ui.image(title='', path=seedpr_img, width='230px')]
    # )

    df = q.user.client_data.dados
    filtered_df = df[(df['CGM'] == q.user.user_inputs.aluno)]
    # filtered_df['Serie'] = filtered_df['Serie'].astype("string")

    image = 'https://images.nightcafe.studio/jobs/3SO0o4E3vquicLfDRrQX/3SO0o4E3vquicLfDRrQX--2--qoj58.jpg?tr=w-1600,c-at_max'

    q.page['side'] = ui.form_card(box='4 2 2 3', items=[
        ui.dropdown(name='aluno_combobox',
                    label='CGM (Aluno)',
                    placeholder='Selecionar Aluno:',
                    value=q.user.user_inputs.aluno,
                    trigger=True,
                    choices=[ui.choice(name=choice, label=choice) for choice in q.user.client_data.aluno]
        ),
        ui.separator(label=''),
        ui.persona(title='Enzo', image=image),
    ])

    # fev = round(filtered_df['FEV'].sum(), 2)
    # mar = round(filtered_df['MAR'].sum(), 2)
    # abr = round(filtered_df['ABR'].sum(), 2)
    # mai = round(filtered_df['MAI'].sum(), 2)
    # jun = round(filtered_df['JUN'].sum(), 2)
    # jul = round(filtered_df['JUL'].sum(), 2)
    # ago = round(filtered_df['AGO'].sum(), 2)
    # set = round(filtered_df['SET'].sum(), 2)
    # out = round(filtered_df['OUT'].sum(), 2)

    # q.page['frequencia'] = ui.plot_card(
    # box='4 5 8 3',
    # title='Frequência registrada no ano',
    # data=data('mes freq', 3, rows=[
    #             ('Fevereiro', fev),
    #             ('Março', mar),
    #             ('Abril', abr),
    #             ('Maio', mai),
    #             ('Junho', jun),
    #             ('Julho', jul),
    #             ('Agosto', ago),
    #             ('Setembro', set),
    #             ('Outubro', out),
    # ]),
    # plot=ui.plot([ui.mark(type='line', x='=mes', y='=freq', curve='step',
    #                       label='={{intl freq minimum_fraction_digits=2 maximum_fraction_digits=2}}')
    #                       ])
    # )

    prob = filtered_df['Prob_Evasao'].values[0]

    q.page['prob_evasao'] = ui.tall_gauge_stat_card(
    box='6 2 2 2',
    title='Probabilidade de evasão',
    value='={{intl foo style="percent" minimum_fraction_digits=2 maximum_fraction_digits=2}}',
    aux_value='={{intl bar style="percent" minimum_fraction_digits=2 maximum_fraction_digits=2}}',
    plot_color='$red',
    progress=prob,
    data=dict(foo=prob)
    )

    rows, columns = get_data_row(q)

    q.page['table'] = ui.form_card(
            box='1 2 3 8',
            items=[
            ui.table(
                name='table',
                columns=columns,
                rows=rows,
                height='680px',
                resettable=True,
                downloadable=True,
                )
    ])

# IRA_1T_22
# IPM_1T_22
# IRA_2T_22
# IPM_2T_22
# IRA_3T_22
# IPM_3T_22
# IRA_1T_23
# IPM_1T_23
# IRA_2T_23
# IPM_2T_23
# IRA_3T_23
# IPM_3T_23

    # edu_fis = round(filtered_df['EDUCACAO FISICA'].sum(), 2)
    # his = round(filtered_df['HISTORIA'].sum(), 2)
    # fil = round(filtered_df['FILOSOFIA'].sum(), 2)
    # fis = round(filtered_df['FISICA'].sum(), 2)
    # bio = round(filtered_df['BIOLOGIA'].sum(), 2)
    # por = round(filtered_df['LINGUA PORTUGUESA'].sum(), 2)
    # qui = round(filtered_df['QUIMICA'].sum(), 2)
    # geo = round(filtered_df['GEOGRAFIA'].sum(), 2)
    # mat = round(filtered_df['MATEMATICA'].sum(), 2)
    # art = round(filtered_df['ARTE'].sum(), 2)


    # q.page['nota_1serie'] = ui.plot_card(
    #     box='4 8 8 3',
    #     title='Quadro de notas do aluno',
    #     data=data('materia nota', 5, rows=[
    #                 ('Educação Fisica', edu_fis),
    #                 ('História', his),
    #         ('Filosofia', fil),
    #         ('Fisica', fis),
    #         ('Biologia', bio),
    #                 ('Português', por),
    #         ('Quimica', qui),
    #                 ('Geografia', geo),
    #                 ('Matemática', mat),
    #                 ('Artes', art),
    #     ]),
    #     plot=ui.plot([ui.mark(type='interval', x='=materia', y='=nota', y_min=0)])
    #     )

    shap_df = filtered_df[[
    "CGM",
    "Prob_Evasao",
    "Resultado.predicted(th=0.34069)",
    "CodMec",
    "CodTurma",
    "IRA_1T_22",
    "IPM_1T_22",
    "IRA_2T_22",
    "IPM_2T_22",
    "IRA_3T_22",
    "IPM_3T_22",
    "IRA_MF_22",
    "IPM_MF_22",
    "IRA_1T_23",
    "IPM_1T_23",
    "IRA_2T_23",
    "IPM_2T_23",
    "IRA_3T_23",
    "IPM_3T_23",
    "IRA_MF_23",
    "IPM_MF_23",
    "NumTurmas22",
    "NumTurmas23",
    "NumEscolas22",
    "NumEscolas23",
    "NumDisciplinas22",
    "NumDisciplinas23",
    "Idade",
    "Sexo",
    "DescNre",
    "DescMun",
    "TipoEstab",
    "Distancia",
    "Aprov22",
    "RepFreq22",
    "RepNota22",
    "RepNotaFreq22",
    "SemRegistros22",
    "contrib_Aprov22",
    "contrib_Bairro",
    "contrib_BolsaFamilia",
    "contrib_CepAluno",
    "contrib_CepEscola",
    "contrib_Cgm",
    "contrib_CodEncam",
    "contrib_CodMec",
    "contrib_CodMun",
    "contrib_CodNre",
    "contrib_CodTurma",
    "contrib_CoordX",
    "contrib_CoordY",
    "contrib_DataNasc",
    "contrib_DescEncam",
    "contrib_DescEscola",
    "contrib_DescMun",
    "contrib_DescNre",
    "contrib_Distancia",
    "contrib_IPM_1T_22",
    "contrib_IPM_1T_23",
    "contrib_IPM_2T_22",
    "contrib_IPM_2T_23",
    "contrib_IPM_3T_22",
    "contrib_IPM_3T_23",
    "contrib_IPM_MF_22",
    "contrib_IPM_MF_23",
    "contrib_IRA_1T_22",
    "contrib_IRA_1T_23",
    "contrib_IRA_2T_22",
    "contrib_IRA_2T_23",
    "contrib_IRA_3T_22",
    "contrib_IRA_3T_23",
    "contrib_IRA_MF_22",
    "contrib_IRA_MF_23",
    "contrib_Idade",
    "contrib_Lat",
    "contrib_Long",
    "contrib_MotivoEncerramento",
    "contrib_MotivoFalta",
    "contrib_Num",
    "contrib_NumDisciplinas22",
    "contrib_NumDisciplinas23",
    "contrib_NumEscolas22",
    "contrib_NumEscolas23",
    "contrib_NumTurmas22",
    "contrib_NumTurmas23",
    "contrib_RepFreq22",
    "contrib_RepNota22",
    "contrib_RepNotaFreq22",
    "contrib_Rua",
    "contrib_SemRegistros22",
    "contrib_Serie",
    "contrib_Sexo",
    "contrib_TFM_22",
    "contrib_TFM_23",
    "contrib_TF_1T_22",
    "contrib_TF_1T_23",
    "contrib_TF_2T_22",
    "contrib_TF_2T_23",
    "contrib_TF_3T_22",
    "contrib_TF_3T_23",
    "contrib_TipoEstab",
    "contrib_bias"
]]

    shap_df = shap_df.melt(id_vars='CGM')

    # estou tendo problemas com esses valores, precisam ser todos transformados em numéricos, porém ao fazer a transformação ignorando os valores estranhos ele aponta somente 2 colunas, pode continuar daqui.

    shap_df['value'] = pd.to_numeric(shap_df['value'], errors='coerce') 


    shap_df = shap_df.sort_values(by=['value'], ascending=False)
    shap_df['variable'] = shap_df['variable'].str.replace('contrib_', '', regex=True)

    shap_df = shap_df[:5]
    shap_df = shap_df.sort_values(by='value', ascending=True)

    rows2 = shap_df[['variable', 'value']].values
    rows2 = [(row[0], row[1]) for row in rows2]

    q.page['shap'] = ui.plot_card(
                box='8 2 4 3',
                title=f'Variáveis de maior contribuição para a previsão de evasão do aluno',
                data=data('feature shapley', len(rows2), rows=rows2),
                plot=ui.plot([ui.mark(type='interval', x='=shapley', y='=feature', y_min=0)])
    )


