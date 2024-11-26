#pragma once

#include <iostream> // for std::cerr
#include <fstream> // for std::ofstream

namespace pdv
{
	static void serialize() noexcept
	{
		std::ofstream stream("result.xml", std::ios::trunc | std::ios::out);
		if(!stream.is_open())
		{
			std::cerr << "Failed to create result.xml file" << std::endl;
			return;
		}
		const std::string_view content = "Hello World";
		stream.write(content.data(), content.size());
		stream.close();
	}
}
