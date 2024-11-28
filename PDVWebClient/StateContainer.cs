using MySql.Data.MySqlClient;

public class EntryData
{
	public int ID { get; set; }
	public uint Index { get; set; }
	public string? Title { get; set; }
	public string? Filename { get; set; }
	public string? Description { get; set; }
	public string? Source { get; set; }
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

    public static string GetDBString(IConfiguration Configuration)
    {
            string databaseServer = Configuration["databaseServer"];
            if(databaseServer == null)
                databaseServer = "local_host";
            string databaseName = Configuration["databaseName"];
            if(databaseName == null)
                databaseName = "db_pdv";
            string databaseUser = Configuration["databaseUser"];
            if(databaseUser == null)
                databaseUser = "pdvwebclient";
            string password = Configuration["dbUserPassword"];
        string connectionString = String.Format("Server={0};Database={1};Uid={2};Pwd={3};", databaseServer, databaseName, databaseUser, password);
        Console.WriteLine(connectionString);
        return connectionString;
    }

 	public void Initialize(IConfiguration Configuration)
 	{
        string connectionString = GetDBString(Configuration);
        using(MySqlConnection connection = new MySqlConnection(connectionString))
        {
            connection.Open();
            Console.WriteLine("Connected to MySQL!");
            string query = string.Format("SELECT * FROM {0}.main_table", Configuration["databaseName"] ?? "db_pdv");
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