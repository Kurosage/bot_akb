import parametr


def get_task_by_numberUEO_id(task_number, type_key):
    type_dict = {'1': 'IdTerm1', '2': 'TaskNumber', '3': 'NumberOutsourcer'}
    try:
        parametr.cursor_terminal.execute(f'''SELECT
                 tt.[TaskNumber]
                 ,tt.[NumberOutsourcer]
                ,tt.[IdTerm1]
                ,tt.[AddOffices]
                ,ttsk.Organization
                 ,SUBSTRING(tt.[PhoneAndContact],9, CHARINDEX('_От Банка',tt.[PhoneAndContact])-9) Contact_TST
                ,tt.[DateOfCreation]
                ,tt.[TaskText]
                ,tt.[TaskDetails]
                ,tt.[PeriodOfExecution] as Kontrolnii_srok
                ,tt.[StatusOutsourcing]
                
                FROM
                test.[dbo].[test_task] tt
                 left join[test].[dbo].[test_task] ttsk on tt.IdTerm1 = ttsk.IdTerm1
                 where
                tt.{type_dict[type_key]} = '{task_number}' and
                tt.[Status] = 0

            ''')
        for row in parametr.cursor_terminal.fetchall():
            print(row)
            return row
    except Exception as e:
        print(e)
        return "Error: Ошибка получения информации о задаче из БД"
    return "Открытая задача с таким номером не найдена."

