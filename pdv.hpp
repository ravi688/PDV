#pragma once

#include <iostream> // for std::cerr
#include <fstream> // for std::ofstream
#include <string_view> // for std::string_view
#include <string> // for std::string
#include <initializer_list> // for std::initializer_list
#include <vector> // for std::vector
#include <utility> // for std::pair

namespace pdv
{
	class metrics
	{
	private:
		std::string m_title;
		struct Entry
		{
			std::pair<std::string, float> output;
			std::vector<std::pair<std::string, float>> inputs;
			Entry(std::pair<std::string, float>&& _output, std::vector<std::pair<std::string, float>>&& _inputs) noexcept : output(std::move(_output)), inputs(std::move(_inputs)) { }
			Entry(Entry&& entry) noexcept : output(std::move(entry.output)), inputs(std::move(entry.inputs)) { }
			Entry(const Entry&) = delete;
		};
		std::vector<Entry> m_entries;
	public:
		metrics(const std::string_view title) noexcept : m_title(title) { }
		metrics(const metrics&) = delete;
		metrics(metrics&&) = delete;
		void add(std::pair<std::string_view, float> output, std::initializer_list<std::pair<std::string_view, float>> inputs) noexcept
		{
			Entry entry { { std::string(output.first), output.second }, { } };
			entry.inputs.reserve(inputs.size());
			for(const auto& pair : inputs)
				entry.inputs.push_back({ std::string(pair.first), pair.second });
			m_entries.push_back(std::move(entry));
		}
		void serialize() noexcept
		{
			std::ofstream stream("result.xml", std::ios::trunc | std::ios::out);
			if(!stream.is_open())
			{
				std::cerr << "Failed to create result.xml file" << std::endl;
				return;
			}
			stream << "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n";
			stream << "<metrics title=\"" << m_title << "\">\n";
			for(Entry& entry : m_entries)
			{
				stream << "\t<output desc=\"" << entry.output.first << "\" value=\"" << entry.output.second << "\"/>\n";
				stream << "\t<inputs>\n";
				for(auto& pair : entry.inputs)
					stream << "\t\t<input desc=\"" << pair.first << "\" value=\"" << pair.second << "\"/>\n";
				stream << "\t</inputs>\n";
			}
			stream << "</metrics>\n";
			stream.close();
		}
	};
}