using MySql.Data.MySqlClient;

public class EntryData
{
	public int ID { get; set; }
	public uint Index { get; set; }
	public string? Title { get; set; }
	public string? Filename { get; set; }
	public string? Description { get; set; }
	public string? Source { get; set; }
	public string? Result { get; set; }
	public bool IsVisible { get; set; }
}

public class StateContainer
{
 	private List<EntryData> entries = new List<EntryData>();

 	public List<EntryData> Entries
 	{
 		get { return entries; }
 		set
 		{
 			entries = value;
 			NotifyStateChanged();
 		}
 	}

 	public event Action? OnChange;

 	private void NotifyStateChanged() => OnChange?.Invoke();

 	public StateContainer()
 	{
        string connectionString = "Server=192.168.1.18;Database=db_pdv;Uid=pdvwebclient;Pwd=Welcome@123;";
        using(MySqlConnection connection = new MySqlConnection(connectionString))
        {
            connection.Open();
            Console.WriteLine("Connected to MySQL!");
            string query = "SELECT * FROM db_pdv.main_table";
            using(MySqlCommand command = new MySqlCommand(query, connection))
            {
                using(MySqlDataReader reader = command.ExecuteReader())
                {
                    uint index = 0;
                    while(reader.Read())
                    {
                        EntryData data = new EntryData();
                        data.ID = (int)reader["id"];
                        data.Index = index;
                        data.Title = reader["title"].ToString();
                        data.Filename = reader["filename"].ToString();
                        data.Description = reader["description"].ToString();
                        data.Source = reader["source"].ToString();
                        data.Result = reader["result"].ToString();
                        data.IsVisible = false;
                        entries.Add(data);
                        ++index;
                    }
                }
            }
        }
        NotifyStateChanged();
 	}
}